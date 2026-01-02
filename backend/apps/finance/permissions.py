"""
Permission classes for Finance app.
"""

from rest_framework import permissions


class IsFinanceUser(permissions.BasePermission):
    """Allows access to finance users and admins."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superuser and admin have full access
        if request.user.is_superuser or request.user.role in ['ADMIN', 'SUPER_ADMIN']:
            return True
        
        # Finance users can be identified by email pattern or a specific role
        # For now, allow admin role users
        return request.user.role in ['ADMIN', 'SUPER_ADMIN']


class IsFinanceUserOrReadOnly(permissions.BasePermission):
    """Allows finance users to modify, others to read."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return IsFinanceUser().has_permission(request, view)


class IsStudentOwner(permissions.BasePermission):
    """Allows students to view their own finance data."""
    
    def has_object_permission(self, request, view, obj):
        # Admin and finance users can access all
        if request.user.is_superuser or request.user.role in ['ADMIN', 'SUPER_ADMIN']:
            return True
        
        # Check if object has student attribute
        student = getattr(obj, 'student', None)
        if not student:
            return False
        
        # Check if user is the student (by email match)
        if hasattr(request.user, 'email') and student.email == request.user.email:
            return True
        
        return False
