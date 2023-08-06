"""
Permissions for viewsets
"""
from rest_framework.permissions import BasePermission


class IsStaffOrSuperuser(BasePermission):
    """
    Give permission for Staff and Superusers only
    """
    def has_permission(self, request, view):
        return request.user.is_active and (request.user.is_staff or request.user.is_superuser)
