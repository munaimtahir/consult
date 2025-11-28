"""
Permission classes for Admin Panel endpoints.
"""

from rest_framework import permissions


class IsSystemAdmin(permissions.BasePermission):
    """
    Allows access only to system administrators (ADMIN role or superuser).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_user


class HasAdminPanelAccess(permissions.BasePermission):
    """
    Allows access only to users who can access the Admin Panel.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_admin_panel_access()


class IsSystemAdminOrHasPermission(permissions.BasePermission):
    """
    Base class for permission checks that allow system admins or users 
    with a specific permission flag.
    
    Usage:
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, CanManageUsers]
    """
    permission_name = None
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        if request.user.is_admin_user:
            return True
            
        if self.permission_name and hasattr(request.user, self.permission_name):
            return getattr(request.user, self.permission_name)
        
        return False


class CanManageUsers(IsSystemAdminOrHasPermission):
    """
    Allows access to users who can manage other users.
    """
    permission_name = 'can_manage_users'


class CanManageDepartments(IsSystemAdminOrHasPermission):
    """
    Allows access to users who can manage departments.
    """
    permission_name = 'can_manage_departments'


class CanViewDepartmentDashboard(permissions.BasePermission):
    """
    Allows access to users who can view department dashboards.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser or request.user.is_admin_user:
            return True
            
        return request.user.can_view_department_dashboard


class CanViewGlobalDashboard(permissions.BasePermission):
    """
    Allows access to users who can view global dashboards.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser or request.user.is_admin_user:
            return True
            
        return request.user.can_view_global_dashboard


class CanManageConsultsGlobally(permissions.BasePermission):
    """
    Allows access to users who can manage consults globally.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        return request.user.can_manage_consults_globally


class CanManagePermissions(permissions.BasePermission):
    """
    Allows access only to users who can modify other users' permission flags.
    This is a SuperAdmin-level permission.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        return request.user.can_manage_permissions
