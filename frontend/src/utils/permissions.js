/**
 * Utility functions for checking user permissions and roles.
 */

/**
 * Check if user has a specific permission
 * @param {Object} user - User object from auth context
 * @param {string} permission - Permission key (e.g., 'can_manage_users')
 * @returns {boolean}
 */
export function hasPermission(user, permission) {
    if (!user) return false;
    if (user.is_superuser || user.is_admin_user) return true;
    return user.permissions?.[permission] === true;
}

/**
 * Check if user is a superadmin
 * @param {Object} user - User object from auth context
 * @returns {boolean}
 */
export function isSuperAdmin(user) {
    if (!user) return false;
    return user.is_superuser === true || user.is_admin_user === true;
}

/**
 * Check if user has admin panel access
 * @param {Object} user - User object from auth context
 * @returns {boolean}
 */
export function hasAdminPanelAccess(user) {
    if (!user) return false;
    if (isSuperAdmin(user)) return true;
    if (user.has_admin_panel_access) return true;
    
    const permissions = user.permissions || {};
    return (
        permissions.can_manage_users ||
        permissions.can_manage_departments ||
        permissions.can_view_department_dashboard ||
        permissions.can_view_global_dashboard ||
        permissions.can_manage_consults_globally ||
        permissions.can_manage_permissions
    );
}

/**
 * Get all permissions the user has
 * @param {Object} user - User object from auth context
 * @returns {Array<string>} Array of permission keys
 */
export function getUserPermissions(user) {
    if (!user) return [];
    if (isSuperAdmin(user)) {
        return [
            'can_manage_users',
            'can_manage_departments',
            'can_view_department_dashboard',
            'can_view_global_dashboard',
            'can_manage_consults_globally',
            'can_manage_permissions',
        ];
    }
    
    const permissions = user.permissions || {};
    return Object.keys(permissions).filter(key => permissions[key] === true);
}

