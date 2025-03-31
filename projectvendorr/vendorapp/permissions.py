from rest_framework import permissions

class IsARTrader(permissions.BasePermission):
    """
    Allows access only to users in the AR Traders group.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="AR Traders").exists()


class IsCustomer(permissions.BasePermission):
    """
    Allows access only to users in the Customers group.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Customers").exists()
