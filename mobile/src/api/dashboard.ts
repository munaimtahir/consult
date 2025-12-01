/**
 * Dashboard API functions.
 */

import apiClient from './client';
import { DepartmentDashboardResponse } from './types';
import { logger } from '../services/logger';

/**
 * Dashboard query parameters.
 */
export interface DashboardParams {
  department_id?: number;
  type?: 'received' | 'sent' | 'all';
  status?: string;
  urgency?: string;
  date_from?: string;
  date_to?: string;
  overdue?: boolean;
  assigned_to?: number;
}

/**
 * Get department dashboard data.
 * This is used for HOD and department-level dashboards.
 */
export async function getDepartmentDashboard(params: DashboardParams = {}): Promise<DepartmentDashboardResponse> {
  logger.apiRequest('GET', '/admin/dashboard/department/', params);
  
  const response = await apiClient.get<DepartmentDashboardResponse>('/admin/dashboard/department/', {
    params,
  });
  
  logger.apiResponse('GET', '/admin/dashboard/department/', 200);
  
  return response.data;
}

/**
 * HOD Dashboard response structure.
 * This is a simplified view of department performance.
 */
export interface HODDashboardData {
  summary: {
    total_today: number;
    pending: number;
    in_progress: number;
    completed: number;
    delayed: number;
  };
  delayed_list: Array<{
    id: number;
    patient_name: string;
    status: string;
    created_at: string;
    last_update: string;
  }>;
  activity: Array<{
    user: string;
    acknowledged: number;
  }>;
}

/**
 * Get HOD dashboard data.
 * Falls back to department dashboard if no specific HOD endpoint exists.
 */
export async function getHODDashboard(): Promise<HODDashboardData> {
  logger.apiRequest('GET', '/admin/dashboard/department/');
  
  try {
    // Try to use the department dashboard endpoint
    const response = await apiClient.get<DepartmentDashboardResponse>('/admin/dashboard/department/');
    
    // Transform the response to HOD dashboard format
    const data = response.data;
    
    const hodData: HODDashboardData = {
      summary: {
        total_today: data.summary.completed_today + data.summary.pending + data.summary.in_progress,
        pending: data.summary.pending,
        in_progress: data.summary.in_progress,
        completed: data.summary.completed_today,
        delayed: data.summary.overdue,
      },
      delayed_list: data.received_consults
        .filter(c => c.is_overdue)
        .map(c => ({
          id: c.id,
          patient_name: c.patient.name,
          status: c.status,
          created_at: c.created_at,
          last_update: c.created_at, // TODO: Use updated_at when available
        })),
      activity: [], // TODO: Aggregate activity data when available
    };
    
    logger.apiResponse('GET', '/admin/dashboard/department/', 200);
    
    return hodData;
  } catch (error) {
    logger.apiError('GET', '/admin/dashboard/department/', error);
    throw error;
  }
}
