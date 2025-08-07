from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    """
    Custom permission to only allow users with the 'manager' role to access a view.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == 'manager'
