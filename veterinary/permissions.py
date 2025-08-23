# permissions.py
from rest_framework import permissions


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


"""
API Endpoints Documentation:

1. MEDICINE STOCK MANAGEMENT:
   - GET /api/v1/inventory/medicine-stocks/ - List all medicine stocks
   - POST /api/v1/inventory/medicine-stocks/ - Create new medicine stock
   - GET /api/v1/inventory/medicine-stocks/{id}/ - Get specific medicine stock
   - PUT/PATCH /api/v1/inventory/medicine-stocks/{id}/ - Update medicine stock
   - DELETE /api/v1/inventory/medicine-stocks/{id}/ - Delete medicine stock
   
   Custom Actions:
   - GET /api/v1/inventory/medicine-stocks/low_stock_alerts/ - Get low stock alerts
   - GET /api/v1/inventory/medicine-stocks/expiry_alerts/ - Get expiry alerts
   - POST /api/v1/inventory/medicine-stocks/bulk_update_stock/ - Bulk update stocks
   - GET /api/v1/inventory/medicine-stocks/{id}/allocation_history/ - Get allocation history

2. USER MEDICINE STOCK MANAGEMENT:
   - GET /api/v1/inventory/user-medicine-stocks/ - List user allocations
   - POST /api/v1/inventory/user-medicine-stocks/ - Allocate medicine to user
   - GET /api/v1/inventory/user-medicine-stocks/{id}/ - Get specific allocation
   - PUT/PATCH /api/v1/inventory/user-medicine-stocks/{id}/ - Update allocation
   - DELETE /api/v1/inventory/user-medicine-stocks/{id}/ - Delete allocation
   
   Custom Actions:
   - GET /api/v1/inventory/user-medicine-stocks/my_allocations/ - Get current user's allocations
   - GET /api/v1/inventory/user-medicine-stocks/low_stock_users/ - Get users with low stock
   - POST /api/v1/inventory/user-medicine-stocks/{id}/use_medicine/ - Record medicine usage
   - POST /api/v1/inventory/user-medicine-stocks/{id}/return_medicine/ - Return medicine
   - GET /api/v1/inventory/user-medicine-stocks/{id}/transaction_history/ - Get transaction history

3. DASHBOARD & ANALYTICS:
   - GET /api/v1/inventory/dashboard/stats/ - Get dashboard statistics
   - GET /api/v1/inventory/dashboard/all_alerts/ - Get all inventory alerts
   - GET /api/v1/inventory/dashboard/medicine_list/ - Get medicine list for dropdowns

Query Parameters for Filtering:

Medicine Stock Filters:
- medicine_name: Filter by medicine name (contains)
- category: Filter by category name (contains)
- medicine_form: Filter by medicine form
- expiry_status: expired, expiring_soon, expiring_week, valid
- stock_level: out_of_stock, low_stock, critical_stock, adequate
- batch_number: Filter by batch number (contains)
- total_quantity__gte/lte: Filter by quantity range
- expiry_date__gte/lte: Filter by expiry date range
- has_allocations: true/false

User Medicine Stock Filters:
- user_name: Filter by user name (contains)
- username: Filter by username (contains)
- medicine_name: Filter by medicine name (contains)
- category: Filter by category name (contains)
- batch_number: Filter by batch number (contains)
- stock_status: below_threshold, critical, adequate, fully_used
- allocation_date__gte/lte: Filter by allocation date range
- allocated_by: Filter by who allocated
- sync_status: true/false
- remaining_quantity__gte/lte: Filter by remaining quantity range

Search Fields:
- Medicine Stock: medicine name, batch number, strength
- User Medicine Stock: username, user full name, medicine name

Ordering Fields:
- Medicine Stock: total_quantity, expiry_date, last_updated
- User Medicine Stock: allocation_date, allocated_quantity, used_quantity
"""
