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
    Allows access only to users who are part of the consult's workflow
    (creating or receiving department) or are administrators.
    """
    message = "This consult does not belong to your department."
    
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admins and SuperAdmins have global access
        if user.is_superuser or user.role in ['ADMIN', 'SUPER_ADMIN'] or user.can_manage_consults_globally:
            return True
            
        # Users in the creating department have access
        if user.department and user.department == obj.requesting_department:
            return True
            
        # Users in the receiving department have access
        if user.department and user.department == obj.target_department:
            return True
            
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
