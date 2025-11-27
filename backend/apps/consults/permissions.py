"""
Permissions for Consults app.
"""

from rest_framework import permissions

class IsDoctor(permissions.BasePermission):
    """
    Allows access only to doctors.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'DOCTOR'

class IsReceptionist(permissions.BasePermission):
    """
    Allows access only to receptionists.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'RECEPTIONIST'

class IsConsultParticipant(permissions.BasePermission):
    """
    Allows access to:
    1. The requester
    2. The assigned doctor
    3. Users in the target department
    4. Users in the requesting department (read-only)
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Requester has full access (subject to other constraints)
        if obj.requester == user:
            return True
            
        # Assigned doctor has full access
        if obj.assigned_to == user:
            return True
            
        # Target department members have access
        if obj.target_department == user.department:
            return True
            
        # Requesting department members have read-only access
        if obj.requesting_department == user.department:
            return request.method in permissions.SAFE_METHODS
            
        return False

class CanAssignConsult(permissions.BasePermission):
    """
    Allows access if user can assign consults (HOD or Admin).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin_user or 
            request.user.is_hod
        )
