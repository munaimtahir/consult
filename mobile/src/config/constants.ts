/**
 * Application-wide constants.
 */

/**
 * Consult status values as defined by the backend.
 */
export const CONSULT_STATUS = {
  PENDING: 'PENDING',
  ACKNOWLEDGED: 'ACKNOWLEDGED',
  IN_PROGRESS: 'IN_PROGRESS',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED',
} as const;

export type ConsultStatus = (typeof CONSULT_STATUS)[keyof typeof CONSULT_STATUS];

/**
 * Human-readable labels for consult statuses.
 */
export const CONSULT_STATUS_LABELS: Record<ConsultStatus, string> = {
  PENDING: 'Pending',
  ACKNOWLEDGED: 'Acknowledged',
  IN_PROGRESS: 'In Progress',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
};

/**
 * Urgency levels for consults.
 */
export const URGENCY_LEVELS = {
  EMERGENCY: 'EMERGENCY',
  URGENT: 'URGENT',
  ROUTINE: 'ROUTINE',
} as const;

export type UrgencyLevel = (typeof URGENCY_LEVELS)[keyof typeof URGENCY_LEVELS];

/**
 * Human-readable labels for urgency levels.
 */
export const URGENCY_LABELS: Record<UrgencyLevel, string> = {
  EMERGENCY: 'Emergency',
  URGENT: 'Urgent',
  ROUTINE: 'Routine',
};

/**
 * Note types for consult notes.
 */
export const NOTE_TYPES = {
  PROGRESS: 'PROGRESS',
  RECOMMENDATION: 'RECOMMENDATION',
  ASSESSMENT: 'ASSESSMENT',
  PLAN: 'PLAN',
  FINAL: 'FINAL',
} as const;

export type NoteType = (typeof NOTE_TYPES)[keyof typeof NOTE_TYPES];

/**
 * Pagination defaults.
 */
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
};

/**
 * User roles.
 */
export const USER_ROLES = {
  DOCTOR: 'DOCTOR',
  DEPARTMENT_USER: 'DEPARTMENT_USER',
  HOD: 'HOD',
  ADMIN: 'ADMIN',
} as const;

export type UserRole = (typeof USER_ROLES)[keyof typeof USER_ROLES];
