/**
 * Color palette for the Consult mobile app.
 * Based on a professional medical/hospital theme.
 */

export const colors = {
  // Primary brand colors
  primary: '#2563EB', // Blue - primary action color
  primaryLight: '#3B82F6',
  primaryDark: '#1D4ED8',
  
  // Secondary colors
  secondary: '#6366F1', // Indigo
  secondaryLight: '#818CF8',
  secondaryDark: '#4F46E5',
  
  // Status colors
  success: '#10B981', // Green
  successLight: '#34D399',
  successDark: '#059669',
  
  warning: '#F59E0B', // Amber
  warningLight: '#FBBF24',
  warningDark: '#D97706',
  
  error: '#EF4444', // Red
  errorLight: '#F87171',
  errorDark: '#DC2626',
  
  info: '#3B82F6', // Blue
  infoLight: '#60A5FA',
  infoDark: '#2563EB',
  
  // Consult status colors
  statusPending: '#F59E0B', // Amber
  statusAcknowledged: '#3B82F6', // Blue
  statusInProgress: '#8B5CF6', // Purple
  statusCompleted: '#10B981', // Green
  statusCancelled: '#6B7280', // Gray
  
  // Urgency colors
  urgencyEmergency: '#EF4444', // Red
  urgencyUrgent: '#F59E0B', // Amber
  urgencyRoutine: '#10B981', // Green
  
  // Neutral colors
  white: '#FFFFFF',
  black: '#000000',
  
  // Gray scale
  gray50: '#F9FAFB',
  gray100: '#F3F4F6',
  gray200: '#E5E7EB',
  gray300: '#D1D5DB',
  gray400: '#9CA3AF',
  gray500: '#6B7280',
  gray600: '#4B5563',
  gray700: '#374151',
  gray800: '#1F2937',
  gray900: '#111827',
  
  // Background colors
  background: '#F9FAFB',
  surface: '#FFFFFF',
  surfaceSecondary: '#F3F4F6',
  
  // Text colors
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  textTertiary: '#9CA3AF',
  textInverse: '#FFFFFF',
  
  // Border colors
  border: '#E5E7EB',
  borderFocus: '#3B82F6',
  
  // Overlay
  overlay: 'rgba(0, 0, 0, 0.5)',
};

/**
 * Get the color for a consult status.
 */
export function getStatusColor(status: string): string {
  switch (status) {
    case 'PENDING':
      return colors.statusPending;
    case 'ACKNOWLEDGED':
      return colors.statusAcknowledged;
    case 'IN_PROGRESS':
      return colors.statusInProgress;
    case 'COMPLETED':
      return colors.statusCompleted;
    case 'CANCELLED':
      return colors.statusCancelled;
    default:
      return colors.gray500;
  }
}

/**
 * Get the color for an urgency level.
 */
export function getUrgencyColor(urgency: string): string {
  switch (urgency) {
    case 'EMERGENCY':
      return colors.urgencyEmergency;
    case 'URGENT':
      return colors.urgencyUrgent;
    case 'ROUTINE':
      return colors.urgencyRoutine;
    default:
      return colors.gray500;
  }
}
