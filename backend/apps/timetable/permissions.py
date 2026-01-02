"""
Permissions for Timetable app.
"""

from rest_framework import permissions


class CanEditTimetable(permissions.BasePermission):
    """Allows editing based on week plan status and user role."""
    
    def has_object_permission(self, request, view, obj):
        """Check if user can edit this week plan."""
        if obj.status == 'DRAFT':
            return True
        if obj.status == 'VERIFIED':
            return request.user.is_admin_user or request.user.is_hod
        if obj.status == 'PUBLISHED':
            return request.user.is_admin_user or request.user.is_hod
        return False


class CanVerifyTimetable(permissions.BasePermission):
    """Allows verification of draft weeks."""
    
    def has_object_permission(self, request, view, obj):
        """Check if user can verify this week plan."""
        if obj.status != 'DRAFT':
            return False
        # Verifier role - can be HOD, Admin, or specific verifier role
        return request.user.is_admin_user or request.user.is_hod


class CanPublishTimetable(permissions.BasePermission):
    """Allows publishing of verified weeks."""
    
    def has_object_permission(self, request, view, obj):
        """Check if user can publish this week plan."""
        if obj.status != 'VERIFIED':
            return False
        # Publisher role - typically HOD or Admin
        return request.user.is_admin_user or request.user.is_hod


class CanRevertTimetable(permissions.BasePermission):
    """Allows reverting verified/published weeks to draft."""
    
    def has_object_permission(self, request, view, obj):
        """Check if user can revert this week plan."""
        if obj.status not in ['VERIFIED', 'PUBLISHED']:
            return False
        return request.user.is_admin_user or request.user.is_hod
