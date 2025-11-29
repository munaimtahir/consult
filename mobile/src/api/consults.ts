/**
 * Consults API functions.
 */

import apiClient from './client';
import {
  ConsultListItem,
  ConsultDetail,
  ConsultNote,
  AddNoteRequest,
  PaginatedResponse,
  ConsultStats,
} from './types';
import { logger } from '../services/logger';

/**
 * Consult list query parameters.
 */
export interface ConsultListParams {
  status?: string;
  urgency?: string;
  view?: 'all' | 'my_department' | 'assigned_to_me' | 'my_requests' | 'pending_assignment';
  is_overdue?: boolean;
  page?: number;
  page_size?: number;
}

/**
 * Get consults assigned to the current user.
 */
export async function getMyConsults(params: ConsultListParams = {}): Promise<PaginatedResponse<ConsultListItem>> {
  logger.apiRequest('GET', '/consults/requests/', params);
  
  const response = await apiClient.get<PaginatedResponse<ConsultListItem>>('/consults/requests/', {
    params: {
      ...params,
      view: 'assigned_to_me',
    },
  });
  
  logger.apiResponse('GET', '/consults/requests/', 200, { count: response.data.count });
  
  return response.data;
}

/**
 * Get consults for the user's department.
 */
export async function getDepartmentConsults(params: ConsultListParams = {}): Promise<PaginatedResponse<ConsultListItem>> {
  logger.apiRequest('GET', '/consults/requests/', params);
  
  const response = await apiClient.get<PaginatedResponse<ConsultListItem>>('/consults/requests/', {
    params: {
      ...params,
      view: 'my_department',
    },
  });
  
  logger.apiResponse('GET', '/consults/requests/', 200, { count: response.data.count });
  
  return response.data;
}

/**
 * Get consults requested by the current user.
 */
export async function getMyRequests(params: ConsultListParams = {}): Promise<PaginatedResponse<ConsultListItem>> {
  logger.apiRequest('GET', '/consults/requests/', params);
  
  const response = await apiClient.get<PaginatedResponse<ConsultListItem>>('/consults/requests/', {
    params: {
      ...params,
      view: 'my_requests',
    },
  });
  
  logger.apiResponse('GET', '/consults/requests/', 200, { count: response.data.count });
  
  return response.data;
}

/**
 * Get a single consult by ID.
 */
export async function getConsultById(id: number): Promise<ConsultDetail> {
  logger.apiRequest('GET', `/consults/requests/${id}/`);
  
  const response = await apiClient.get<ConsultDetail>(`/consults/requests/${id}/`);
  
  logger.apiResponse('GET', `/consults/requests/${id}/`, 200);
  
  return response.data;
}

/**
 * Acknowledge a consult.
 */
export async function acknowledgeConsult(id: number): Promise<ConsultDetail> {
  logger.apiRequest('POST', `/consults/requests/${id}/acknowledge/`);
  
  const response = await apiClient.post<ConsultDetail>(`/consults/requests/${id}/acknowledge/`);
  
  logger.apiResponse('POST', `/consults/requests/${id}/acknowledge/`, 200);
  
  return response.data;
}

/**
 * Complete a consult.
 */
export async function completeConsult(id: number): Promise<ConsultDetail> {
  logger.apiRequest('POST', `/consults/requests/${id}/complete/`);
  
  const response = await apiClient.post<ConsultDetail>(`/consults/requests/${id}/complete/`);
  
  logger.apiResponse('POST', `/consults/requests/${id}/complete/`, 200);
  
  return response.data;
}

/**
 * Cancel a consult.
 */
export async function cancelConsult(id: number): Promise<ConsultDetail> {
  logger.apiRequest('POST', `/consults/requests/${id}/cancel/`);
  
  const response = await apiClient.post<ConsultDetail>(`/consults/requests/${id}/cancel/`);
  
  logger.apiResponse('POST', `/consults/requests/${id}/cancel/`, 200);
  
  return response.data;
}

/**
 * Assign a consult to a user.
 */
export async function assignConsult(id: number, assignedToId: number): Promise<ConsultDetail> {
  logger.apiRequest('POST', `/consults/requests/${id}/assign/`, { assigned_to: assignedToId });
  
  const response = await apiClient.post<ConsultDetail>(`/consults/requests/${id}/assign/`, {
    assigned_to: assignedToId,
  });
  
  logger.apiResponse('POST', `/consults/requests/${id}/assign/`, 200);
  
  return response.data;
}

/**
 * Add a note to a consult.
 */
export async function addNoteToConsult(id: number, note: AddNoteRequest): Promise<ConsultNote> {
  logger.apiRequest('POST', `/consults/requests/${id}/add_note/`, note);
  
  const response = await apiClient.post<ConsultNote>(`/consults/requests/${id}/add_note/`, note);
  
  logger.apiResponse('POST', `/consults/requests/${id}/add_note/`, 201);
  
  return response.data;
}

/**
 * Get dashboard statistics for consults.
 */
export async function getConsultStats(): Promise<ConsultStats> {
  logger.apiRequest('GET', '/consults/requests/dashboard_stats/');
  
  const response = await apiClient.get<ConsultStats>('/consults/requests/dashboard_stats/');
  
  logger.apiResponse('GET', '/consults/requests/dashboard_stats/', 200);
  
  return response.data;
}
