/**
 * TypeScript interfaces for API responses and requests.
 * Based on the Django backend models and serializers.
 */

// ============================================
// User & Authentication Types
// ============================================

export interface UserPermissions {
  can_manage_users: boolean;
  can_manage_departments: boolean;
  can_view_department_dashboard: boolean;
  can_view_global_dashboard: boolean;
  can_manage_consults_globally: boolean;
  can_manage_permissions: boolean;
}

export interface DepartmentInfo {
  id: number;
  name: string;
  code: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  designation: string;
  designation_display: string;
  department: number | null;
  department_name: string | null;
  department_info: DepartmentInfo | null;
  seniority_level: number;
  phone_number: string;
  profile_photo: string;
  is_on_call: boolean;
  is_hod: boolean;
  is_admin_user: boolean;
  can_assign_consults: boolean;
  has_admin_panel_access: boolean;
  permissions: UserPermissions;
  is_active: boolean;
  date_joined: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

// ============================================
// Patient Types
// ============================================

export interface Patient {
  id: number;
  name: string;
  mrn: string;
  date_of_birth?: string;
  gender?: string;
  ward?: string;
  bed_number?: string;
  location?: string;
  phone_number?: string;
  emergency_contact?: string;
}

// ============================================
// Department Types
// ============================================

export interface Department {
  id: number;
  name: string;
  code: string;
  description?: string;
  phone?: string;
  email?: string;
  emergency_sla?: number;
  urgent_sla?: number;
  routine_sla?: number;
  is_active: boolean;
}

// ============================================
// Consult Types
// ============================================

export interface ConsultNote {
  id: number;
  consult: number;
  author: number;
  author_name: string;
  author_designation: string;
  note_type: string;
  content: string;
  recommendations: string;
  follow_up_required: boolean;
  follow_up_instructions: string;
  is_final: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConsultListItem {
  id: number;
  patient: number;
  patient_name: string;
  patient_mrn: string;
  patient_location: string;
  requester: number;
  requester_name: string;
  requesting_department: number;
  requesting_department_name: string;
  target_department: number;
  target_department_name: string;
  assigned_to: number | null;
  assigned_to_name: string | null;
  status: string;
  urgency: string;
  reason_for_consult: string;
  is_overdue: boolean;
  notes_count: number;
  created_at: string;
  acknowledged_at: string | null;
  completed_at: string | null;
  expected_response_time: string | null;
}

export interface ConsultDetail {
  id: number;
  patient: Patient;
  requester: User;
  requesting_department: Department;
  target_department: Department;
  assigned_to: User | null;
  status: string;
  urgency: string;
  reason_for_consult: string;
  clinical_question: string;
  relevant_history: string;
  current_medications: string;
  vital_signs: string;
  lab_results: string;
  is_overdue: boolean;
  escalation_level: number;
  created_at: string;
  updated_at: string;
  acknowledged_at: string | null;
  completed_at: string | null;
  expected_response_time: string | null;
  time_elapsed: number | null;
  time_to_acknowledgement: number | null;
  time_to_completion: number | null;
  sla_compliance: boolean;
  notes: ConsultNote[];
}

export interface AddNoteRequest {
  content: string;
  note_type?: string;
  recommendations?: string;
  follow_up_required?: boolean;
  follow_up_instructions?: string;
  is_final?: boolean;
}

export interface UpdateStatusRequest {
  status: string;
}

// ============================================
// Dashboard Types
// ============================================

export interface DashboardSummary {
  total_active: number;
  pending: number;
  acknowledged: number;
  in_progress: number;
  completed_today: number;
  overdue: number;
  sent_active?: number;
}

export interface DashboardConsult {
  id: number;
  patient: {
    id: number;
    name: string;
    mrn: string;
    location: string;
  };
  requesting_department: {
    id: number;
    name: string;
  };
  target_department: {
    id: number;
    name: string;
  };
  assigned_to: {
    id: number;
    name: string;
  } | null;
  created_at: string;
  urgency: string;
  status: string;
  completed_at: string | null;
  is_overdue: boolean;
  reason_for_consult: string;
}

export interface DepartmentDashboardResponse {
  department: {
    id: number;
    name: string;
    code: string;
  };
  summary: DashboardSummary;
  received_consults: DashboardConsult[];
  sent_consults: DashboardConsult[];
}

export interface ConsultStats {
  my_department: {
    pending: number;
    in_progress: number;
    overdue: number;
    total_active: number;
  };
  assigned_to_me: {
    pending: number;
    in_progress: number;
    overdue: number;
  };
  my_requests: {
    pending: number;
    in_progress: number;
    completed: number;
  };
}

// ============================================
// Device & Notification Types
// ============================================

export interface DeviceRegistrationRequest {
  device_id: string;
  fcm_token: string;
  platform: 'android' | 'ios';
}

export interface DeviceRegistrationResponse {
  id: number;
  device_id: string;
  fcm_token: string;
  platform: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================
// Pagination Types
// ============================================

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ============================================
// Error Types
// ============================================

export interface ApiError {
  detail?: string;
  error?: string;
  message?: string;
  [key: string]: unknown;
}
