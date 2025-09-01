# permissions.py
from rest_framework import permissions
from .choices.choices import ActionTypeChoices

class IsMedicineManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only medicine managers to edit stock,
    but allow read access to authenticated users.
    """

    def has_permission(self, request, view):
        # Allow read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions for staff or users with specific permission
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.has_perm("medicine.change_medicinestock")
            )
        )


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to allow users to access only their own medicine allocations,
    unless they are staff.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Staff can access any allocation
        if request.user.is_staff:
            return True

        # Users can only access their own allocations
        return obj.user == request.user


from rest_framework import permissions


class HierarchyPermissionMixin:
    """
    Mixin providing reusable methods for checking user hierarchy and permissions.
    Can be used in any permission class that needs to verify supervisor-subordinate relationships.
    """
    MANAGEMENT_HIERARCHY = {
        'admin': ['it', 'engineering', 'pes'],
        'hr': ['support'],
        'it': ['support'],
        'pes': ['doctor', 'veterinarian', 'mait'], 
        'doctor': ['veterinarian', 'mait'],
        'veterinarian': ['mait'],
        'sales': [],  # Can only manage own department
        'engineering': [],  # Can only manage own department
    }
        
    def is_supervisor_of(self, supervisor, subordinate, max_levels=5):
        """
        Check if supervisor has authority over subordinate using UserProfile hierarchy.
        Supports multi-level hierarchy traversal up to max_levels.
        
        Args:
            supervisor: User object who might be a supervisor
            subordinate: User object who might be a subordinate
            max_levels: Maximum levels to traverse up the hierarchy (default: 5)
            
        Returns:
            bool: True if supervisor has authority over subordinate
        """
        if supervisor == subordinate:
            return True
            
        try:
            subordinate_profile = getattr(subordinate, 'profile', None)
            if not subordinate_profile:
                return False
            
            # Check direct and multi-level reporting relationships
            if self._check_reporting_hierarchy(supervisor, subordinate_profile, max_levels):
                return True
            
            # Check department-based permissions for staff members
            if self._check_department_permissions(supervisor, subordinate_profile):
                return True
            
            return False
            
        except Exception:
            # Fallback to basic staff check
            return supervisor.is_staff and not subordinate.is_staff
    
    def _check_reporting_hierarchy(self, supervisor, subordinate_profile, max_levels):
        """Check direct and multi-level reporting relationships."""
        current_profile = subordinate_profile
        levels_checked = 0
        
        while current_profile and current_profile.reports_to and levels_checked < max_levels:
            if current_profile.reports_to.user == supervisor:
                return True
            current_profile = current_profile.reports_to
            levels_checked += 1
        
        return False
    
    def _check_department_permissions(self, supervisor, subordinate_profile):
        """Check department-based management permissions for staff members."""
        if not supervisor.is_staff:
            return False
            
        supervisor_profile = getattr(supervisor, 'profile', None)
        if not supervisor_profile or not subordinate_profile:
            return False
        
        supervisor_dept = supervisor_profile.department
        subordinate_dept = subordinate_profile.department
        
        # Same department
        if supervisor_dept == subordinate_dept:
            return True
        
        # Check management hierarchy
        if supervisor_dept in self.MANAGEMENT_HIERARCHY:
            return subordinate_dept in self.MANAGEMENT_HIERARCHY[supervisor_dept]
        
        return False
    
    def can_user_access_object(self, user, target_user, method='GET'):
        """
        Check if user can access objects belonging to target_user.
        
        Args:
            user: The requesting user
            target_user: The user who owns the object
            method: HTTP method (for different permission levels)
            
        Returns:
            bool: True if access is allowed
        """
        # Superuser has all permissions
        if user.is_superuser:
            return True
        
        # Users can access their own objects
        if user == target_user:
            return True
        
        # Check supervisor relationship
        return self.is_supervisor_of(user, target_user)


class BaseMedicinePermission(permissions.BasePermission, HierarchyPermissionMixin):
    """
    Base permission class for medicine-related operations.
    Provides common authentication and hierarchy checking functionality.
    """
    
    def has_permission(self, request, view):
        """Basic authentication check."""
        return request.user.is_authenticated
    
    def get_target_user_from_object(self, obj):
        """
        Extract the target user from an object.
        Override this method in subclasses to handle different object types.
        """
        if hasattr(obj, 'user_medicine_stock'):
            return obj.user_medicine_stock.user
        elif hasattr(obj, 'user'):
            return obj.user
        return None


class CanManageMedicineTransactions(BaseMedicinePermission):
    """
    Permission to check if user can manage medicine transactions.
    - Superusers: Can manage all transactions
    - Staff/Managers: Can manage transactions for their subordinates
    - Users: Can only view their own transactions
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        target_user = self.get_target_user_from_object(obj)
        
        if not target_user:
            return False
        
        # Superuser has all permissions
        if user.is_superuser:
            return True
        
        # For read operations
        if request.method in permissions.SAFE_METHODS:
            return self.can_user_access_object(user, target_user, method='GET')
        
        # For write operations
        if request.method in ['POST', 'PUT', 'PATCH']:
            # Supervisors can perform write operations
            if self.is_supervisor_of(user, target_user):
                return True
            
            # Users can create USED transactions for their own stock
            if (target_user == user and 
                view.action in ['create'] and 
                request.data.get('action') == ActionTypeChoices.USED):
                return True
        
        return False


class CanCreateTransactions(BaseMedicinePermission):
    """Permission specifically for creating transactions"""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Only apply additional checks for create action
        if view.action != 'create':
            return True
        
        return self._can_create_transaction(request)
    
    def _can_create_transaction(self, request):
        """Check if user can create a transaction for the specified stock."""
        user_medicine_stock_id = request.data.get('user_medicine_stock')
        if not user_medicine_stock_id:
            return False
        
        try:
            from .models import UserMedicineStock
            stock = UserMedicineStock.objects.select_related(
                'user__profile'
            ).get(id=user_medicine_stock_id)
            
            user = request.user
            stock_user = stock.user
            
            # Superuser can create any transaction
            if user.is_superuser:
                return True
            
            # Check supervisor relationship
            if self.is_supervisor_of(user, stock_user):
                return True
            
            # Users can create USED transactions for their own stock
            action = request.data.get('action')
            if stock_user == user and action == ActionTypeChoices.USED:
                return True
            
            return False
            
        except Exception:
            return False


class UserHierarchyChecker(HierarchyPermissionMixin):
    """
    Standalone utility class for checking user hierarchies outside of DRF permissions.
    Can be used in views, serializers, or other parts of the application.
    """
    
    def __init__(self, max_hierarchy_levels=5):
        self.max_hierarchy_levels = max_hierarchy_levels
    
    def get_subordinates(self, supervisor, max_levels=None):
        """
        Get all subordinates of a supervisor up to max_levels.
        This could be useful for filtering querysets.
        """
        if max_levels is None:
            max_levels = self.max_hierarchy_levels
        
        # This would need to be implemented based on your User/Profile model structure
        # Example implementation:
        subordinates = []
        # Implementation would go here...
        return subordinates
    
    def get_accessible_users(self, user):
        """
        Get all users that the given user can access (themselves + subordinates).
        Useful for filtering data in views.
        """
        accessible_users = [user]  # User can always access themselves
        
        if user.is_superuser:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.all()
        
        # Add subordinates
        accessible_users.extend(self.get_subordinates(user))
        return accessible_users



class CanManageUserStock(permissions.BasePermission):
    """
    Permission class for UserMedicineStock operations.
    - Users can view their own stock
    - Supervisors can manage subordinates' stock
    - Staff can allocate/manage based on hierarchy
    """
    
    def __init__(self):
        self.hierarchy_checker = UserHierarchyChecker()
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        stock_user = obj.user
        
        # Superuser has all permissions
        if user.is_superuser:
            return True
        
        # Users can always access their own stock
        if user == stock_user:
            return True
        
        # For read operations - supervisors can view subordinates' stock
        if request.method in permissions.SAFE_METHODS:
            return self.hierarchy_checker.is_supervisor_of(user, stock_user)
        
        # For write operations - only supervisors can manage subordinates' stock
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return self.hierarchy_checker.is_supervisor_of(user, stock_user)
        
        return False

