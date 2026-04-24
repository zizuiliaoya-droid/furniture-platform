"""Custom permission classes."""
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Only allow users with ADMIN role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'ADMIN')
