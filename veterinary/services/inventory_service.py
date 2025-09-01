# services/inventory_service.py
"""
Business logic layer for inventory operations
Separates business logic from views for better testability and reusability
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import F, Q, Count, Sum
from typing import Dict, List, Optional, Any



class InventoryService:
    """Service class for inventory business logic"""
    
    @staticmethod
    def get_base_filters(request) -> Dict[str, Any]:
        """Extract and validate common filter parameters"""
        return {
            'locale': request.GET.get("locale", "en"),
            'is_active': request.GET.get("is_active", "true").lower() == "true",
            'is_deleted': request.GET.get("is_deleted", "false").lower() == "true",
            'threshold': int(request.GET.get("threshold", 10)),
            'days': int(request.GET.get("days", 30)),
            'location_id': request.GET.get("location_id", None),
        }
    
    @staticmethod
    def get_filtered_querysets(filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get all filtered querysets in one place"""
        from ..models.stock_models import Medicine, MedicineStock, UserMedicineStock
        
        # Base medicine queryset
        medicines_qs = Medicine.objects.filter(
            is_active=filters['is_active'],
            is_deleted=filters['is_deleted'],
            locale=filters['locale'],
        )
        
        # Stock queryset with location filter
        stock_filter = Q(
            medicine__in=medicines_qs,
            is_active=filters['is_active'],
            is_deleted=filters['is_deleted'],
            locale=filters['locale'],
        )
        
        if filters['location_id']:
            stock_filter &= Q(location_id=filters['location_id'])
        
        stock_qs = MedicineStock.objects.filter(stock_filter)
        
        # User stock queryset
        user_stock_qs = UserMedicineStock.objects.filter(
            medicine_stock__in=stock_qs,
            is_active=filters['is_active'],
            is_deleted=filters['is_deleted'],
            locale=filters['locale'],
        )
        
        return {
            'medicines': medicines_qs,
            'stock': stock_qs,
            'user_stock': user_stock_qs,
        }
    
    @staticmethod
    def calculate_dashboard_stats(querysets: Dict, filters: Dict) -> Dict[str, int]:
        """Calculate dashboard statistics"""
        from ..models.stock_models import UserMedicineStock  # Import here to avoid circular imports
        
        medicines_qs = querysets['medicines']
        stock_qs = querysets['stock']
        user_stock_qs = querysets['user_stock']
        
        # For methods that require manager access, apply the same filters 
        # to the manager method results
        base_user_filters = Q(
            medicine_stock__in=querysets['stock'],
            is_active=filters['is_active'],
            is_deleted=filters['is_deleted'],
            locale=filters['locale'],
        )
        
        return {
            "total_medicines": medicines_qs.count(),
            "total_stock_items": stock_qs.count(),
            "total_user_allocations": user_stock_qs.count(),
            "expired_stock_count": stock_qs.expired().count(),
            "expiring_soon_count": stock_qs.expiring(days=filters['days']).count(),
            "low_stock_count": stock_qs.low_stock(threshold=filters['threshold']).count(),
            "critical_user_stock_count": UserMedicineStock.active.get_critical_stock().filter(base_user_filters).count(),
            "low_user_stock_count": UserMedicineStock.active.get_low_stock().filter(base_user_filters).count(),
            "healthy_user_stock_count": UserMedicineStock.active.get_healthy_stock().filter(base_user_filters).count(),
        }


class QuerySetManagerBridge:
    """
    Helper class to bridge the gap between QuerySets and Manager methods
    Provides a clean way to apply manager methods to existing querysets
    """
    
    @staticmethod
    def apply_manager_method_to_queryset(model_class, manager_method_name, queryset, **method_kwargs):
        """
        Apply a manager method to an existing queryset
        
        Args:
            model_class: The model class (e.g., UserMedicineStock)
            manager_method_name: Name of the manager method (e.g., 'get_critical_stock')
            queryset: Existing queryset to filter
            **method_kwargs: Arguments to pass to the manager method
        
        Returns:
            Combined queryset with both manager method and original filters
        """
        # Get the manager method result
        manager_method = getattr(model_class.objects, manager_method_name)
        manager_queryset = manager_method(**method_kwargs)
        
        # Combine with existing queryset using intersection
        return manager_queryset.filter(id__in=queryset.values_list('id', flat=True))
    
    @staticmethod
    def get_user_stock_alerts(user_stock_base_qs):
        """
        Example usage of the bridge pattern for user stock alerts
        """
        from ..models.stock_models import UserMedicineStock
        
        # Get different types of problematic stocks using manager methods
        critical_stocks = QuerySetManagerBridge.apply_manager_method_to_queryset(
            UserMedicineStock, 'get_critical_stock', user_stock_base_qs
        )
        
        low_stocks = QuerySetManagerBridge.apply_manager_method_to_queryset(
            UserMedicineStock, 'get_low_stock', user_stock_base_qs
        )
        
        out_of_stock = QuerySetManagerBridge.apply_manager_method_to_queryset(
            UserMedicineStock, 'get_out_of_stock', user_stock_base_qs
        )
        
        return {
            'critical': critical_stocks,
            'low': low_stocks, 
            'out_of_stock': out_of_stock
        }


class AlertService:
    """Service class for generating inventory alerts"""

    SEVERITY_ORDER = {"expired": 0, "critical": 1, "warning": 2}
    
    @staticmethod
    def generate_all_alerts(querysets: Dict, filters: Dict) -> List[Dict]:
        """Generate all types of alerts"""
        alerts = []
        
        # Generate different types of alerts
        alerts.extend(AlertService._generate_stock_alerts(querysets['stock'], filters))
        alerts.extend(AlertService._generate_expiry_alerts(querysets['stock'],exp_days=filters['days']))
        alerts.extend(AlertService._generate_user_stock_alerts(querysets['user_stock']))
        
        # Sort by severity
        alerts.sort(key=lambda x: AlertService.SEVERITY_ORDER.get(x["severity"], 3))
        
        return alerts
    
    @staticmethod
    def _generate_stock_alerts(stock_qs, filters: Dict) -> List[Dict]:
        """Generate global stock level alerts"""
        alerts = []
        threshold = filters['threshold']
        
        low_stocks = stock_qs.with_available_qty().low_stock(threshold=threshold).select_related(
            "medicine", "medicine__category"
        )
        
        for stock in low_stocks:
            available = stock.available_qty or stock.total_quantity
            alerts.append({
                "type": "global_stock",
                "severity": "critical" if available <= 5 else "warning",
                "medicine_name": stock.medicine.medicine,
                "medicine_strength": stock.medicine.strength or "",
                "current_quantity": available,
                "threshold_quantity": threshold,
                "unit_of_quantity": stock.medicine.category.unit_of_quantity,
                "batch_number": stock.batch_number,
                "message": f"Low global stock: {available} {stock.medicine.category.unit_of_quantity} remaining",
            })
        
        return alerts
    
    @staticmethod
    def _generate_expiry_alerts(stock_qs,exp_days) -> List[Dict]:
        """Generate expiry alerts"""
        alerts = []
        today = timezone.now().date()
        
        expiring_stocks = stock_qs.expiring(days=exp_days).select_related(
            "medicine", "medicine__category"
        )
        
        for stock in expiring_stocks:
            days = (stock.expiry_date - today).days
            severity = AlertService._get_expiry_severity(days)
            
            alerts.append({
                "type": "global_stock",
                "severity": severity,
                "medicine_name": stock.medicine.medicine,
                "medicine_strength": stock.medicine.strength or "",
                "current_quantity": stock.total_quantity,
                "unit_of_quantity": stock.medicine.category.unit_of_quantity,
                "batch_number": stock.batch_number,
                "expiry_date": stock.expiry_date,
                "days_to_expiry": days,
                "message": f"{'Expired' if days < 0 else 'Expiring in'} {abs(days)} days",
            })
        
        return alerts
    
    @staticmethod
    def _generate_user_stock_alerts(user_stock_qs) -> List[Dict]:
        """Generate user stock alerts"""
        from ..models.stock_models import UserMedicineStock
        alerts = []
        
        # We can't call manager methods on a queryset, so we need to recreate the logic
        # or use the manager method on the model class with appropriate filters
        
        # Option 1: Use manager method with filters (recommended)
        # Get the same base filters that were applied to user_stock_qs
        low_user_stocks = UserMedicineStock.objects.get_low_stock().filter(
            id__in=user_stock_qs.values_list('id', flat=True)
        ).select_related(
            "user", "medicine_stock__medicine", "medicine_stock__medicine__category"
        )
        
        # Also get critical stocks
        critical_user_stocks = UserMedicineStock.objects.get_critical_stock().filter(
            id__in=user_stock_qs.values_list('id', flat=True)
        ).select_related(
            "user", "medicine_stock__medicine", "medicine_stock__medicine__category"
        )
        
        # Combine and process both low and critical stocks
        all_problem_stocks = low_user_stocks.union(critical_user_stocks)
        
        for stock in all_problem_stocks:
            remaining = stock.allocated_quantity - stock.used_quantity
            threshold_val = max(stock.min_threshold, stock.threshold_quantity)
            
            alerts.append({
                "type": "user_stock",
                "severity": "critical" if remaining <= threshold_val * 0.5 else "warning",
                "medicine_name": stock.medicine_stock.medicine.medicine,
                "medicine_strength": stock.medicine_stock.medicine.strength or "",
                "current_quantity": remaining,
                "threshold_quantity": threshold_val,
                "unit_of_quantity": stock.medicine_stock.medicine.category.unit_of_quantity,
                "user_name": stock.user.get_full_name(),
                "message": f"{stock.user.get_full_name()} - Low stock: {remaining} {stock.medicine_stock.medicine.category.unit_of_quantity} remaining",
            })
        
        return alerts
    
    @staticmethod
    def _get_expiry_severity(days: int) -> str:
        """Determine severity based on days to expiry"""
        if days < 0:
            return "expired"
        elif days <= 7:
            return "critical"
        else:
            return "warning"

# validators.py
"""
Input validation utilities
"""
from rest_framework.exceptions import ValidationError


class InventoryValidators:
    """Validators for inventory-related inputs"""
    
    @staticmethod
    def validate_threshold(threshold_str: str) -> int:
        """Validate and convert threshold parameter"""
        try:
            threshold = int(threshold_str)
            if threshold < 0:
                raise ValidationError("Threshold must be non-negative")
            return threshold
        except (ValueError, TypeError):
            raise ValidationError("Invalid threshold value")
    
    @staticmethod
    def validate_days(days_str: str) -> int:
        """Validate and convert days parameter"""
        try:
            days = int(days_str)
            if days < 1 or days > 365:
                raise ValidationError("Days must be between 1 and 365")
            return days
        except (ValueError, TypeError):
            raise ValidationError("Invalid days value")



# validators.py
"""
Input validation utilities
"""
from rest_framework.exceptions import ValidationError


class InventoryValidators:
    """Validators for inventory-related inputs"""
    
    @staticmethod
    def validate_threshold(threshold_str: str) -> int:
        """Validate and convert threshold parameter"""
        try:
            threshold = int(threshold_str)
            if threshold < 0:
                raise ValidationError("Threshold must be non-negative")
            return threshold
        except (ValueError, TypeError):
            raise ValidationError("Invalid threshold value")
    
    @staticmethod
    def validate_days(days_str: str) -> int:
        """Validate and convert days parameter"""
        try:
            days = int(days_str)
            if days < 1 or days > 365:
                raise ValidationError("Days must be between 1 and 365")
            return days
        except (ValueError, TypeError):
            raise ValidationError("Invalid days value")
