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


class IsVendor(permissions.BasePermission):
    """
    Allows access only to users in the Vendor group.
    Also ensures vendors can only access their own data.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Vendor").exists()
    
    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        # Check if the object belongs to the vendor
        try:
            vendor = request.user.vendor_set.first()
            return vendor and obj.vendor == vendor
        except:
            return False
