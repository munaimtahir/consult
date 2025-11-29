/**
 * Permission helper functions for UI-level permission checks.
 */

import { User, UserPermissions } from '../api/types';
import { USER_ROLES } from './constants';

/**
 * Checks if the user can view the department consults tab.
 */
export function canViewDepartmentConsults(user: User | null): boolean {
  if (!user) return false;
  
  return (
    user.permissions?.can_view_department_dashboard === true ||
    user.is_hod === true ||
    user.role === USER_ROLES.HOD ||
    user.role === USER_ROLES.ADMIN ||
    user.is_admin_user === true
  );
}

/**
 * Checks if the user can view the HOD dashboard.
 */
export function canViewHODDashboard(user: User | null): boolean {
  if (!user) return false;
  
  return (
    user.permissions?.can_view_department_dashboard === true ||
    user.permissions?.can_view_global_dashboard === true ||
    user.is_hod === true ||
    user.role === USER_ROLES.HOD ||
    user.role === USER_ROLES.ADMIN ||
    user.is_admin_user === true
  );
}

/**
 * Checks if the user can acknowledge consults.
 */
export function canAcknowledgeConsult(user: User | null): boolean {
  if (!user) return false;
  return true; // Any authenticated user in the target department can acknowledge
}

/**
 * Checks if the user can assign consults to others.
 */
export function canAssignConsults(user: User | null): boolean {
  if (!user) return false;
  
  return (
    user.can_assign_consults === true ||
    user.is_hod === true ||
    user.role === USER_ROLES.HOD ||
    user.role === USER_ROLES.ADMIN
  );
}

/**
 * Checks if the user can add notes to a consult.
 */
export function canAddNotes(user: User | null): boolean {
  if (!user) return false;
  return true; // Any authenticated user can add notes if they have access to the consult
}

/**
 * Checks if the user can update consult status.
 */
export function canUpdateConsultStatus(user: User | null): boolean {
  if (!user) return false;
  return true; // Allowed for assigned users or department members
}

/**
 * Returns a summary of user permissions for display.
 */
export function getPermissionsSummary(user: User | null): {
  hodAccess: boolean;
  departmentView: boolean;
  globalView: boolean;
  canAssign: boolean;
} {
  if (!user) {
    return {
      hodAccess: false,
      departmentView: false,
      globalView: false,
      canAssign: false,
    };
  }

  return {
    hodAccess: canViewHODDashboard(user),
    departmentView: canViewDepartmentConsults(user),
    globalView: user.permissions?.can_view_global_dashboard === true,
    canAssign: canAssignConsults(user),
  };
}
