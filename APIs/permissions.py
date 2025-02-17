from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.get("role") == "admin"

class IsManager(BasePermission):
    """
    Allows access only to managers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.get("role") == "manager"

from rest_framework.permissions import BasePermission

class IsMongoAuthenticated(BasePermission):
    """Allow access if request.user is a MongoDB user and authenticated"""

    def has_permission(self, request, view):
        print(f"🔍 Checking MongoDB authentication for user: {request.user}")

        # ✅ Check if user is properly assigned and authenticated
        if hasattr(request, "user") and request.user is not None:
            return request.user.is_authenticated
        
        return False  # ❌ Reject if user is missing or not authenticated
