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

from rest_framework.permissions import BasePermission

class IsMongoAuthenticated(BasePermission):
    """
    Allows access only to authenticated MongoDB users.
    """

    def has_permission(self, request, view):
        user = getattr(request, "_force_auth_user", request.user)  # ✅ Check forced user

        print(f"🔍 Checking MongoDB authentication for user: {user}")

        if user.is_authenticated:
            print(f"✅ Access Granted for {user}")
            return True

        print("❌ Unauthorized Access Attempt")
        return False
