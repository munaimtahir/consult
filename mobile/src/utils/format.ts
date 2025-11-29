/**
 * Formatting utilities for display.
 */

import { CONSULT_STATUS_LABELS, URGENCY_LABELS, ConsultStatus, UrgencyLevel } from '../config/constants';

/**
 * Format a consult status for display.
 */
export function formatStatus(status: string): string {
  return CONSULT_STATUS_LABELS[status as ConsultStatus] || status;
}

/**
 * Format an urgency level for display.
 */
export function formatUrgency(urgency: string): string {
  return URGENCY_LABELS[urgency as UrgencyLevel] || urgency;
}

/**
 * Format a user's full name.
 */
export function formatUserName(firstName?: string, lastName?: string): string {
  const parts = [firstName, lastName].filter(Boolean);
  return parts.length > 0 ? parts.join(' ') : 'Unknown User';
}

/**
 * Truncate text to a maximum length with ellipsis.
 */
export function truncateText(text: string | null | undefined, maxLength: number): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength - 3)}...`;
}

/**
 * Format a patient location string.
 */
export function formatPatientLocation(ward?: string, bed?: string): string {
  const parts = [ward, bed].filter(Boolean);
  return parts.length > 0 ? parts.join(' - ') : 'Unknown location';
}

/**
 * Format a phone number for display.
 */
export function formatPhoneNumber(phone: string | null | undefined): string {
  if (!phone) return 'N/A';
  
  // Simple formatting - add more complex logic if needed
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  } else if (cleaned.length === 11 && cleaned.startsWith('1')) {
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  
  return phone;
}

/**
 * Format a number with comma separators.
 */
export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '0';
  return num.toLocaleString('en-US');
}

/**
 * Capitalize the first letter of a string.
 */
export function capitalize(text: string | null | undefined): string {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

/**
 * Convert a snake_case or SCREAMING_SNAKE_CASE string to Title Case.
 */
export function snakeToTitleCase(text: string | null | undefined): string {
  if (!text) return '';
  return text
    .toLowerCase()
    .split('_')
    .map(word => capitalize(word))
    .join(' ');
}
