from rest_framework.permissions import BasePermission, IsAuthenticated as DRFIsAuthenticated


class IsAdminOrRestaurantManager(BasePermission):
    """
    Allows access only to Admin, GeneralManager, or Manager roles.
    """

    def has_permission(self, request, view):
        role = getattr(request.user, 'role', None)
        return role in ('Admin', 'GeneralManager', 'Manager')


# Expose DRF's IsAuthenticated directly for convenience
IsAuthenticated = DRFIsAuthenticated
