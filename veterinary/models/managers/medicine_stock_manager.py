from django.db import models, transaction
from django.utils import timezone
from django.db.models import F, Q, Sum, Count, Case, When, Value, DecimalField,ExpressionWrapper,DurationField
from django.utils import timezone
from datetime import timedelta
from ...choices.choices import SyncStatusChoices,ApprovalStatusChoices

# -----------------------------
# Custom QuerySet / Manager
# -----------------------------

from django.db import models
from django.db.models import (
    F, Q, Sum, Count, Avg, Max, Min, Case, When, Value, 
    DecimalField, IntegerField, DurationField, ExpressionWrapper
)
from django.utils import timezone
from decimal import Decimal


class MedicineStockQuerySet(models.QuerySet):
    """Enhanced QuerySet for MedicineStock with comprehensive filtering and aggregation methods"""
    
    # === BASIC ANNOTATIONS ===
    
    def with_available_qty(self):
        """Annotate with available quantity calculations"""
        return self.annotate(
            allocated_quantity=Sum("user_allocations__allocated_quantity") or Value(0, DecimalField()),
            available_qty=F("total_quantity") - F("reserved_quantity"),
            utilization_rate=Case(
                When(total_quantity=0, then=Value(0)),
                default=F("reserved_quantity") * 100 / F("total_quantity"),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        )
    
    def with_allocation_stats(self):
        """Annotate with user allocation statistics"""
        return self.annotate(
            total_allocated=Sum("user_allocations__allocated_quantity") or Value(0),
            total_used=Sum("user_allocations__used_quantity") or Value(0),
            allocation_count=Count("user_allocations"),
            unique_users=Count("user_allocations__user", distinct=True),
            pending_allocations=Count(
                "user_allocations", 
                filter=Q(user_allocations__sync_status='PENDING')
            )
        )
    
    def with_expiry_info(self):
        """Annotate with expiry-related calculations"""
        today = timezone.now().date()
        return self.annotate(
            days_to_expiry=Case(
                When(expiry_date__isnull=True, then=Value(None)),
                default=ExpressionWrapper(
                    F("expiry_date") - today, 
                    output_field=DurationField()
                )
            ),
            is_expired=Case(
                When(expiry_date__lt=today, then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField()
            ),
            expiry_status=Case(
                When(expiry_date__isnull=True, then=Value('No Expiry')),
                When(expiry_date__lt=today, then=Value('Expired')),
                When(expiry_date__lte=today + timedelta(days=30), then=Value('Expiring Soon')),
                When(expiry_date__lte=today + timedelta(days=90), then=Value('Warning')),
                default=Value('Good'),
                output_field=models.CharField()
            )
        )

    # === STOCK LEVEL FILTERING ===
    def non_expired(self):
        """Convenience method to exclude expired medicines"""
        return self.with_expiry_info().filter(is_expired=False)

    def low_stock(self, threshold=10):
        """Filter stocks below threshold (excluding expired)"""
        return self.with_available_qty().with_expiry_info().filter(
            Q(available_qty__lte=threshold) |
            Q(available_qty__isnull=True, total_quantity__lte=threshold),
            is_expired=False
        )

    def critical_stock(self, threshold=5):
        """Filter critically low stocks (excluding expired)"""
        return self.with_available_qty().with_expiry_info().filter(
            Q(available_qty__lte=threshold) |
            Q(available_qty__isnull=True, total_quantity__lte=threshold),
            is_expired=False
        )

    def out_of_stock(self):
        """Filter completely out of stock items (excluding expired)"""
        return self.with_available_qty().with_expiry_info().filter(
            Q(available_qty__lte=0) |
            Q(total_quantity__lte=0),
            is_expired=False
        )

    def healthy_stock(self, threshold=10):
        """Filter stocks above warning threshold (excluding expired)"""
        return self.with_available_qty().with_expiry_info().filter(
            available_qty__gt=threshold,
            is_expired=False
        )

    def overstocked(self, threshold=1000):
        """Filter overstocked items above threshold"""
        return self.with_available_qty().filter(available_qty__gte=threshold)


    # === EXPIRY FILTERING ===
    
    def expired(self):
        """Filter expired stocks"""
        today = timezone.now().date()
        return self.filter(expiry_date__lt=today)
    
    def expiring(self, days=30):
        """Filter stocks expiring within specified days"""
        today = timezone.now().date()
        future_date = today + timedelta(days=days)
        return self.with_expiry_info().filter(
            expiry_date__lte=future_date, 
            expiry_date__gte=today
        )
    
    def expiring_soon(self, days=7):
        """Filter stocks expiring very soon"""
        return self.expiring(days=days)
    
    def no_expiry(self):
        """Filter stocks without expiry date"""
        return self.filter(expiry_date__isnull=True)
    
    def valid_stock(self):
        """Filter non-expired stocks"""
        today = timezone.now().date()
        return self.filter(
            Q(expiry_date__gte=today) | Q(expiry_date__isnull=True)
        )
    
    # === LOCATION AND ORGANIZATION ===
    
    def by_location(self, location_id):
        """Filter by specific location"""
        return self.filter(location_id=location_id)
    
    def by_locations(self, location_ids):
        """Filter by multiple locations"""
        return self.filter(location_id__in=location_ids)
    
    def by_medicine(self, medicine_id):
        """Filter by specific medicine"""
        return self.filter(medicine_id=medicine_id)
    
    def by_medicines(self, medicine_ids):
        """Filter by multiple medicines"""
        return self.filter(medicine_id__in=medicine_ids)
    
    def by_medicine_category(self, category_name):
        """Filter by medicine category"""
        return self.filter(medicine__category__name__icontains=category_name)
    
    def by_batch(self, batch_number):
        """Filter by batch number"""
        return self.filter(batch_number__icontains=batch_number)
    
    # === RESERVATION AND ALLOCATION ===
    
    def fully_reserved(self):
        """Filter stocks that are fully reserved"""
        return self.with_available_qty().filter(available_qty__lte=0)
    
    def partially_reserved(self):
        """Filter stocks that are partially reserved"""
        return self.filter(
            reserved_quantity__gt=0,
            reserved_quantity__lt=F('total_quantity')
        )
    
    def unreserved(self):
        """Filter stocks with no reservations"""
        return self.filter(reserved_quantity=0)
    
    def high_utilization(self, threshold=80):
        """Filter stocks with high utilization rate"""
        return self.with_available_qty().filter(utilization_rate__gte=threshold)
    
    def with_allocations(self):
        """Filter stocks that have user allocations"""
        return self.filter(user_allocations__isnull=False).distinct()
    
    def without_allocations(self):
        """Filter stocks without any user allocations"""
        return self.filter(user_allocations__isnull=True)
    
    # === RECENT ACTIVITY ===
    
    def recently_updated(self, days=7):
        """Filter stocks updated recently"""
        recent_date = timezone.now() - timedelta(days=days)
        return self.filter(last_updated__gte=recent_date)
    
    def recently_added(self, days=7):
        """Filter stocks added recently"""
        recent_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=recent_date)
    
    def stale_stock(self, days=90):
        """Filter stocks not updated for long time"""
        stale_date = timezone.now() - timedelta(days=days)
        return self.filter(last_updated__lt=stale_date)
    
    # === AGGREGATION METHODS ===
    
    def total_value_stats(self):
        """Get total value statistics"""
        return self.with_available_qty().aggregate(
            total_stock_quantity=Sum('total_quantity'),
            total_reserved_quantity=Sum('reserved_quantity'),
            total_available_quantity=Sum('available_qty'),
            unique_medicines=Count('medicine', distinct=True),
            unique_locations=Count('location', distinct=True),
            unique_batches=Count('batch_number', distinct=True),
            avg_utilization=Avg('utilization_rate')
        )
    
    def location_summary(self):
        """Get summary by location"""
        return self.with_available_qty().values(
            'location__name', 'location_id'
        ).annotate(
            total_stocks=Count('id'),
            total_quantity=Sum('total_quantity'),
            available_quantity=Sum('available_qty'),
            reserved_quantity=Sum('reserved_quantity'),
            unique_medicines=Count('medicine', distinct=True),
            low_stock_count=Count(Case(
                When(available_qty__lte=10, then=1),
                output_field=IntegerField()
            )),
            expired_count=Count(Case(
                When(expiry_date__lt=timezone.now().date(), then=1),
                output_field=IntegerField()
            ))
        ).order_by('location__name')
    
    def medicine_summary(self):
        """Get summary by medicine"""
        return self.with_available_qty().values(
            'medicine__medicine', 'medicine__category__name', 'medicine_id'
        ).annotate(
            total_batches=Count('id'),
            total_quantity=Sum('total_quantity'),
            available_quantity=Sum('available_qty'),
            reserved_quantity=Sum('reserved_quantity'),
            locations_count=Count('location', distinct=True),
            earliest_expiry=Min('expiry_date'),
            latest_expiry=Max('expiry_date')
        ).order_by('medicine__medicine')
    
    def expiry_report(self):
        """Get expiry analysis report"""
        today = timezone.now().date()
        return self.with_available_qty().aggregate(
            expired_count=Count(Case(
                When(expiry_date__lt=today, then=1),
                output_field=IntegerField()
            )),
            expired_quantity=Sum(Case(
                When(expiry_date__lt=today, then=F('available_qty')),
                default=0, output_field=DecimalField()
            )),
            expiring_7_days=Count(Case(
                When(
                    expiry_date__gte=today,
                    expiry_date__lte=today + timedelta(days=7),
                    then=1
                ),
                output_field=IntegerField()
            )),
            expiring_30_days=Count(Case(
                When(
                    expiry_date__gte=today,
                    expiry_date__lte=today + timedelta(days=30),
                    then=1
                ),
                output_field=IntegerField()
            )),
            no_expiry_count=Count(Case(
                When(expiry_date__isnull=True, then=1),
                output_field=IntegerField()
            ))
        )


class MedicineStockManager(models.Manager):
    """Enhanced Manager for MedicineStock with comprehensive business methods"""
   
    def get_queryset(self):
        return MedicineStockQuerySet(self.model, using=self._db)
    # def get_queryset(self):
    #     """
    #     Override get_queryset to apply default filtering/optimization
    #     You can customize this based on your needs
    #     """
    #     # Example: Always select related fields for performance
    #     return super().get_queryset()
        
    # === QUERYSET METHOD PROXIES ===
    
    def with_available_qty(self):
        return self.get_queryset().with_available_qty()
    
    def with_allocation_stats(self):
        return self.get_queryset().with_allocation_stats()
    
    def with_expiry_info(self):
        return self.get_queryset().with_expiry_info()
    
    # Stock Level Methods
    def low_stock(self, threshold=10):
        return self.get_queryset().low_stock(threshold=threshold)
    
    def critical_stock(self, threshold=5):
        return self.get_queryset().critical_stock(threshold=threshold)
    
    def out_of_stock(self):
        return self.get_queryset().out_of_stock()
    
    def healthy_stock(self, min_threshold=10, max_threshold=1000):
        return self.get_queryset().healthy_stock(min_threshold, max_threshold)
    
    # Expiry Methods
    def expired(self):
        return self.get_queryset().expired()
    
    def expiring(self, days=30):
        return self.get_queryset().expiring(days=days)
    
    def expiring_soon(self, days=7):
        return self.get_queryset().expiring_soon(days=days)
    
    def valid_stock(self):
        return self.get_queryset().valid_stock()
    
    # Location Methods
    def by_location(self, location_id):
        return self.get_queryset().by_location(location_id)
    
    def by_locations(self, location_ids):
        return self.get_queryset().by_locations(location_ids)
    
    # === BUSINESS LOGIC METHODS ===
    
    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics"""
        base_stats = self.with_available_qty().total_value_stats()
        expiry_stats = self.expiry_report()
        
        return {
            **base_stats,
            **expiry_stats,
            'critical_stock_count': self.critical_stock().count(),
            'low_stock_count': self.low_stock().count(),
            'out_of_stock_count': self.out_of_stock().count(),
            'fully_reserved_count': self.get_queryset().fully_reserved().count(),
        }
    
    #=== To get the dashoboard data location wise ===#
    def get_location_dashboard(self, location_id):
        """Get dashboard stats for specific location"""
        return self.by_location(location_id).with_available_qty().aggregate(
            total_stocks=Count('id'),
            total_medicines=Count('medicine', distinct=True),
            total_quantity=Sum('total_quantity'),
            available_quantity=Sum('available_qty'),
            reserved_quantity=Sum('reserved_quantity'),
            low_stock_count=Count(Case(
                When(available_qty__lte=10, then=1),
                output_field=IntegerField()
            )),
            expired_count=Count(Case(
                When(expiry_date__lt=timezone.now().date(), then=1),
                output_field=IntegerField()
            )),
            expiring_soon_count=Count(Case(
                When(
                    expiry_date__gte=timezone.now().date(),
                    expiry_date__lte=timezone.now().date() + timedelta(days=7),
                    then=1
                ),
                output_field=IntegerField()
            ))
        )
    
    def get_medicine_availability(self, medicine_id, location_id=None):
        """Get availability info for a specific medicine"""
        queryset = self.filter(medicine_id=medicine_id).valid_stock()
        
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        return queryset.with_available_qty().aggregate(
            total_available=Sum('available_qty') or Decimal('0'),
            total_reserved=Sum('reserved_quantity') or Decimal('0'),
            batch_count=Count('id'),
            location_count=Count('location', distinct=True),
            earliest_expiry=Min('expiry_date')
        )
    
    def find_alternative_stock(self, medicine_id, required_quantity, exclude_location=None):
        """Find alternative stock locations for a medicine"""
        queryset = self.filter(medicine_id=medicine_id).valid_stock().with_available_qty()
        
        if exclude_location:
            queryset = queryset.exclude(location_id=exclude_location)
        
        return queryset.filter(
            available_qty__gte=required_quantity
        ).select_related('location', 'medicine').order_by(
            'expiry_date', '-available_qty'
        )
    
    def get_reorder_list(self, low_stock_threshold=10):
        """Get medicines that need reordering"""
        return self.with_available_qty().values(
            'medicine__medicine',
            'medicine__category__name',
            'medicine_id'
        ).annotate(
            total_available=Sum('available_qty'),
            location_count=Count('location', distinct=True)
        ).filter(
            total_available__lte=low_stock_threshold
        ).order_by('total_available')
    
    def get_wastage_report(self, days=30):
        """Get expired stock wastage report"""
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        return self.expired().filter(
            expiry_date__gte=cutoff_date
        ).with_available_qty().values(
            'medicine__medicine',
            'location__name',
            'batch_number',
            'expiry_date'
        ).annotate(
            wasted_quantity=F('available_qty')
        ).order_by('-expiry_date')
    
    def bulk_reserve_stock(self, reservations):
        """
        Bulk reserve stock for multiple items
        reservations: list of dicts with 'stock_id' and 'quantity' keys
        """
        successful_reservations = []
        failed_reservations = []
        
        for reservation in reservations:
            try:
                stock = self.get(id=reservation['stock_id'])
                stock.reserve_stock(reservation['quantity'])
                successful_reservations.append(reservation['stock_id'])
            except (self.model.DoesNotExist, ValueError) as e:
                failed_reservations.append({
                    'stock_id': reservation['stock_id'],
                    'error': str(e)
                })
        
        return {
            'successful': successful_reservations,
            'failed': failed_reservations
        }
    
    def get_transfer_candidates(self, medicine_id, target_location_id, required_quantity):
        """Find best candidates for stock transfer"""
        return self.filter(
            medicine_id=medicine_id
        ).exclude(
            location_id=target_location_id
        ).valid_stock().with_available_qty().filter(
            available_qty__gte=required_quantity
        ).select_related(
            'location', 'medicine'
        ).order_by('expiry_date', '-available_qty')


class UserMedicineStockManager(models.Manager):
    """
    Custom manager for UserMedicineStock with business logic methods
    """
    
    def get_queryset(self):
        """
        Override get_queryset to apply default filtering/optimization
        You can customize this based on your needs
        """
        # Example: Always select related fields for performance
        return super().get_queryset().select_related(
            'user', 
            'medicine_stock__medicine'
        )
        
    # === STOCK STATUS QUERIES ===


    def get_critical_stock(self, user=None):
        """Get stocks that are at or below minimum threshold"""
        queryset = self.annotate(
            available_quantity=F("allocated_quantity") - F("used_quantity")
        ).filter(
            available_quantity__lte=F("min_threshold")
        )

        if user:
            queryset = queryset.filter(user=user)

        return queryset.select_related("user", "medicine_stock__medicine")

    def get_out_of_stock(self, user=None):
        """Get stocks that are completely depleted"""
        queryset = self.filter(
            used_quantity__gte=F("allocated_quantity")
        )

        if user:
            queryset = queryset.filter(user=user)

        return queryset.select_related("user", "medicine_stock__medicine")

    def get_low_stock(self, user=None):
        """Get stocks that are below warning threshold but above critical"""
        queryset = self.annotate(
            available_quantity=F("allocated_quantity") - F("used_quantity")
        ).filter(
            available_quantity__lte=F("threshold_quantity"),
            available_quantity__gt=F("min_threshold")
        )

        if user:
            queryset = queryset.filter(user=user)

        return queryset.select_related("user", "medicine_stock__medicine")

    def get_healthy_stock(self, user=None):
        """Get stocks that are above warning threshold"""
        queryset = self.annotate(
            available_quantity=F("allocated_quantity") - F("used_quantity")
        ).filter(
            available_quantity__gt=F("threshold_quantity")
        )

        if user:
            queryset = queryset.filter(user=user)

        return queryset.select_related("user", "medicine_stock__medicine")

    # === EXPIRY RELATED QUERIES ===
    
    def get_expired_stock(self, user=None):
        """Get stocks with expired medicines"""
        queryset = self.filter(
            medicine_stock__expiry_date__lt=timezone.now().date()
        )
        
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset.select_related('user', 'medicine_stock__medicine')
    
    def get_expiring_soon(self, days=30, user=None):
        """Get stocks expiring within specified days (default 30 days)"""
        expiry_date = timezone.now().date() + timedelta(days=days)
        queryset = self.filter(
            medicine_stock__expiry_date__lte=expiry_date,
            medicine_stock__expiry_date__gte=timezone.now().date()
        )
        
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset.select_related('user', 'medicine_stock__medicine')
    
    # === USER SPECIFIC QUERIES ===
    
    def get_user_stocks(self, user, include_depleted=False):
        """Get all stocks for a specific user"""
        queryset = self.filter(user=user)
        
        if not include_depleted:
            queryset = queryset.filter(used_quantity__lt=F('allocated_quantity'))
        
        return queryset.select_related('medicine_stock__medicine')
    
    def get_user_stock_summary(self, user):
        """Get stock summary for a user"""
        return self.filter(user=user).aggregate(
            total_allocations=Count('id'),
            total_allocated_value=Sum('allocated_quantity'),
            total_used_value=Sum('used_quantity'),
            remaining_value=Sum(F('allocated_quantity') - F('used_quantity')),
            critical_count=Count(
                Case(
                    When(
                        allocated_quantity__minus=F('used_quantity') <= F('min_threshold'),
                        then=Value(1)
                    ),
                    output_field=models.IntegerField()
                )
            ),
            warning_count=Count(
                Case(
                    When(
                        Q(allocated_quantity__minus=F('used_quantity') <= F('threshold_quantity')) &
                        Q(allocated_quantity__minus=F('used_quantity') > F('min_threshold')),
                        then=Value(1)
                    ),
                    output_field=models.IntegerField()
                )
            )
        )
    
    # === SYNC STATUS QUERIES ===
    
    def get_pending_sync(self, user=None):
        """Get records pending synchronization"""
        queryset = self.filter(sync_status='PENDING')
        
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset
    
    def get_failed_sync(self, user=None):
        """Get records with failed synchronization"""
        queryset = self.filter(sync_status='FAILED')
        
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset
    
    # === ALLOCATION QUERIES ===
    
    def get_recent_allocations(self, days=7, user=None):
        """Get allocations made in recent days (default 7 days)"""
        recent_date = timezone.now().date() - timedelta(days=days)
        queryset = self.filter(allocation_date__gte=recent_date)
        
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset.select_related('user', 'medicine_stock__medicine', 'allocated_by')
    
    def get_allocations_by_medicine(self, medicine_name=None, medicine_id=None):
        """Get all allocations for a specific medicine"""
        if medicine_id:
            return self.filter(medicine_stock__medicine__id=medicine_id)
        elif medicine_name:
            return self.filter(medicine_stock__medicine__medicine__icontains=medicine_name)
        else:
            raise ValueError("Either medicine_name or medicine_id must be provided")
    
    # === DASHBOARD & ANALYTICS QUERIES ===
    
    def get_dashboard_summary(self):
        """Get overall dashboard summary statistics"""
        return self.aggregate(
            total_stocks=Count('id'),
            total_users=Count('user', distinct=True),
            critical_stocks=Count(
                Case(
                    When(
                        allocated_quantity__minus=F('used_quantity') <= F('min_threshold'),
                        then=Value(1)
                    ),
                    output_field=models.IntegerField()
                )
            ),
            warning_stocks=Count(
                Case(
                    When(
                        Q(allocated_quantity__minus=F('used_quantity') <= F('threshold_quantity')) &
                        Q(allocated_quantity__minus=F('used_quantity') > F('min_threshold')),
                        then=Value(1)
                    ),
                    output_field=models.IntegerField()
                )
            ),
            out_of_stock=Count(
                Case(
                    When(used_quantity__gte=F('allocated_quantity'), then=Value(1)),
                    output_field=models.IntegerField()
                )
            ),
            pending_sync=Count(
                Case(
                    When(sync_status='PENDING', then=Value(1)),
                    output_field=models.IntegerField()
                )
            )
        )
    
    def get_top_users_by_allocation(self, limit=10):
        """Get top users by total allocated quantity"""
        return self.values('user__username', 'user__first_name', 'user__last_name') \
                  .annotate(
                      total_allocated=Sum('allocated_quantity'),
                      total_used=Sum('used_quantity'),
                      remaining=Sum(F('allocated_quantity') - F('used_quantity')),
                      stock_count=Count('id')
                  ) \
                  .order_by('-total_allocated')[:limit]
    
    # === UTILITY METHODS ===
    
    def get_stocks_needing_attention(self, user=None):
        """Get all stocks that need attention (critical, expired, failed sync)"""
        queryset = self.filter(
            Q(allocated_quantity__minus=F('used_quantity') <= F('min_threshold')) |
            Q(medicine_stock__expiry_date__lt=timezone.now().date()) |
            Q(sync_status='FAILED')
        )
        
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset.select_related('user', 'medicine_stock__medicine')
    
    def bulk_update_usage(self, usage_data):
        """
        Bulk update used quantities
        usage_data: list of dicts with 'id' and 'used_quantity' keys
        """
        stocks_to_update = []
        
        for data in usage_data:
            try:
                stock = self.get(id=data['id'])
                stock.used_quantity = data['used_quantity']
                stock.sync_status = 'PENDING'  # Mark for sync
                stocks_to_update.append(stock)
            except self.model.DoesNotExist:
                continue
        
        if stocks_to_update:
            self.bulk_update(
                stocks_to_update, 
                ['used_quantity', 'sync_status'], 
                batch_size=100
            )
        
        return len(stocks_to_update)
    
    def mark_sync_status(self, stock_ids, status):
        """Bulk update sync status for given stock IDs"""
        return self.filter(id__in=stock_ids).update(sync_status=status)
    
    def get_medicine_usage_report(self, start_date=None, end_date=None):
        """Generate medicine usage report within date range"""
        queryset = self
        
        if start_date:
            queryset = queryset.filter(allocation_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(allocation_date__lte=end_date)
        
        return queryset.values(
            'medicine_stock__medicine__medicine',
            'medicine_stock__medicine__category'
        ).annotate(
            total_allocated=Sum('allocated_quantity'),
            total_used=Sum('used_quantity'),
            total_remaining=Sum(F('allocated_quantity') - F('used_quantity')),
            user_count=Count('user', distinct=True),
            allocation_count=Count('id')
        ).order_by('-total_used')
        
    def with_remaining(self):
        """Annotate with remaining quantity"""
        return self.annotate(
            remaining=F('allocated_quantity') - F('used_quantity')
        )


# ============== ADDITIONAL MANAGER PATTERNS ==============

class ActiveUserMedicineStockManager(UserMedicineStockManager):
    """Manager that only returns active/non-depleted AND approved stocks"""
    
    def get_queryset(self):
        return super().get_queryset().filter(
            used_quantity__lt=F('allocated_quantity'),
            approval_status=ApprovalStatusChoices.APPROVED  # Add this
        )


class OptimizedUserMedicineStockManager(UserMedicineStockManager):
    """Manager with heavy optimization for read-heavy operations - approved stocks only"""
    
    def get_queryset(self):
        return super().get_queryset().filter(
            approval_status=ApprovalStatusChoices.APPROVED  # Add this
        ).select_related(
            'user', 
            'medicine_stock__medicine',
            'allocated_by',
            'approved_by'  # Include approved_by for optimization
        ).prefetch_related(
            'medicine_stock__medicine__category'
        )


class PendingApprovalManager(models.Manager):
    """Manager for stocks pending approval"""
    def get_queryset(self):
        return super().get_queryset().filter(
            approval_status=ApprovalStatusChoices.PENDING
        )


class RejectedStockManager(models.Manager):
    """Manager for rejected stocks (for audit purposes)"""
    def get_queryset(self):
        return super().get_queryset().filter(
            approval_status=ApprovalStatusChoices.REJECTED
        )