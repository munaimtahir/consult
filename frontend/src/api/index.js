import apiClient from './client';

export const authAPI = {
    login: async (email, password) => {
        const response = await apiClient.post('/auth/token/', {
            email,
            password,
        });
        return response.data;
    },

    getCurrentUser: async () => {
        const response = await apiClient.get('/auth/users/me/');
        return response.data;
    },

    refreshToken: async (refreshToken) => {
        const response = await apiClient.post('/auth/token/refresh/', {
            refresh: refreshToken,
        });
        return response.data;
    },
};

export const consultsAPI = {
    getConsults: async (params = {}) => {
        const response = await apiClient.get('/consults/requests/', { params });
        return response.data;
    },

    getConsult: async (id) => {
        const response = await apiClient.get(`/consults/requests/${id}/`);
        return response.data;
    },

    createConsult: async (data) => {
        const response = await apiClient.post('/consults/requests/', data);
        return response.data;
    },

    acknowledgeConsult: async (id) => {
        const response = await apiClient.post(`/consults/requests/${id}/acknowledge/`);
        return response.data;
    },

    assignConsult: async (id, assignedTo) => {
        const response = await apiClient.post(`/consults/requests/${id}/assign/`, {
            assigned_to: assignedTo,
        });
        return response.data;
    },

    addNote: async (id, noteData) => {
        const response = await apiClient.post(`/consults/requests/${id}/add_note/`, noteData);
        return response.data;
    },

    completeConsult: async (id) => {
        const response = await apiClient.post(`/consults/requests/${id}/complete/`);
        return response.data;
    },

    getDashboardStats: async () => {
        const response = await apiClient.get('/consults/requests/dashboard_stats/');
        return response.data;
    },
};

export const departmentsAPI = {
    getDepartments: async () => {
        const response = await apiClient.get('/departments/');
        return response.data;
    },
};

export const patientsAPI = {
    getPatients: async (params = {}) => {
        const response = await apiClient.get('/patients/', { params });
        return response.data;
    },

    createPatient: async (data) => {
        const response = await apiClient.post('/patients/', data);
        return response.data;
    },
};

// Admin Panel APIs
export const adminAPI = {
    // Users management
    getUsers: async (params = {}) => {
        const response = await apiClient.get('/admin/users/', { params });
        return response.data;
    },

    getUser: async (id) => {
        const response = await apiClient.get(`/admin/users/${id}/`);
        return response.data;
    },

    createUser: async (data) => {
        const response = await apiClient.post('/admin/users/', data);
        return response.data;
    },

    updateUser: async (id, data) => {
        const response = await apiClient.patch(`/admin/users/${id}/`, data);
        return response.data;
    },

    activateUser: async (id) => {
        const response = await apiClient.post(`/admin/users/${id}/activate/`);
        return response.data;
    },

    deactivateUser: async (id) => {
        const response = await apiClient.post(`/admin/users/${id}/deactivate/`);
        return response.data;
    },

    updateUserPermissions: async (id, permissions) => {
        const response = await apiClient.patch(`/admin/users/${id}/update_permissions/`, permissions);
        return response.data;
    },

    setUserPassword: async (id, password) => {
        const response = await apiClient.post(`/admin/users/${id}/set_password/`, { password });
        return response.data;
    },

    // Departments management
    getDepartments: async (params = {}) => {
        const response = await apiClient.get('/admin/departments/', { params });
        return response.data;
    },

    getDepartment: async (id) => {
        const response = await apiClient.get(`/admin/departments/${id}/`);
        return response.data;
    },

    createDepartment: async (data) => {
        const response = await apiClient.post('/admin/departments/', data);
        return response.data;
    },

    updateDepartment: async (id, data) => {
        const response = await apiClient.patch(`/admin/departments/${id}/`, data);
        return response.data;
    },

    deleteDepartment: async (id) => {
        const response = await apiClient.delete(`/admin/departments/${id}/`);
        return response.data;
    },

    activateDepartment: async (id) => {
        const response = await apiClient.post(`/admin/departments/${id}/activate/`);
        return response.data;
    },

    deactivateDepartment: async (id) => {
        const response = await apiClient.post(`/admin/departments/${id}/deactivate/`);
        return response.data;
    },

    getDepartmentUsers: async (id) => {
        const response = await apiClient.get(`/admin/departments/${id}/users/`);
        return response.data;
    },

    getDepartmentHierarchy: async () => {
        const response = await apiClient.get('/admin/departments/hierarchy/');
        return response.data;
    },

    // Dashboard APIs
    getDepartmentDashboard: async (params = {}) => {
        const response = await apiClient.get('/admin/dashboards/department/', { params });
        return response.data;
    },

    getGlobalDashboard: async (params = {}) => {
        const response = await apiClient.get('/admin/dashboards/global/', { params });
        return response.data;
    },

    getDoctorAnalytics: async () => {
        const response = await apiClient.get('/admin/analytics/doctors/');
        return response.data;
    },

    getDepartmentOverview: async (id) => {
        const response = await apiClient.get(`/admin/departments/${id}/overview/`);
        return response.data;
    },

    // Consult management
    reassignConsult: async (id, data) => {
        const response = await apiClient.post(`/admin/consults/${id}/reassign/`, data);
        return response.data;
    },

    forceCloseConsult: async (id, data) => {
        const response = await apiClient.post(`/admin/consults/${id}/force-close/`, data);
        return response.data;
    },

    // Email notification settings
    getEmailNotificationSettings: async (params = {}) => {
        const response = await apiClient.get('/admin/email-notification-settings/', { params });
        return response.data;
    },

    getEmailNotificationSetting: async (id) => {
        const response = await apiClient.get(`/admin/email-notification-settings/${id}/`);
        return response.data;
    },

    createEmailNotificationSetting: async (data) => {
        const response = await apiClient.post('/admin/email-notification-settings/', data);
        return response.data;
    },

    updateEmailNotificationSetting: async (id, data) => {
        const response = await apiClient.patch(`/admin/email-notification-settings/${id}/`, data);
        return response.data;
    },

    // SMTP configurations
    getSMTPConfigurations: async () => {
        const response = await apiClient.get('/admin/smtp-configurations/');
        return response.data;
    },

    getSMTPConfiguration: async (id) => {
        const response = await apiClient.get(`/admin/smtp-configurations/${id}/`);
        return response.data;
    },

    createSMTPConfiguration: async (data) => {
        const response = await apiClient.post('/admin/smtp-configurations/', data);
        return response.data;
    },

    updateSMTPConfiguration: async (id, data) => {
        const response = await apiClient.patch(`/admin/smtp-configurations/${id}/`, data);
        return response.data;
    },

    activateSMTPConfiguration: async (id) => {
        const response = await apiClient.post(`/admin/smtp-configurations/${id}/activate/`);
        return response.data;
    },

    deactivateSMTPConfiguration: async (id) => {
        const response = await apiClient.post(`/admin/smtp-configurations/${id}/deactivate/`);
        return response.data;
    },

    testSMTPConnection: async (id) => {
        const response = await apiClient.post(`/admin/smtp-configurations/${id}/test_connection/`);
        return response.data;
    },
};

export const timetableAPI = {
    // Week plans
    getWeeks: async (params = {}) => {
        const response = await apiClient.get('/timetable/weeks/', { params });
        return response.data;
    },

    getWeek: async (id) => {
        const response = await apiClient.get(`/timetable/weeks/${id}/`);
        return response.data;
    },

    createWeek: async (weekStartDate) => {
        const response = await apiClient.post('/timetable/weeks/create_week/', {
            week_start_date: weekStartDate,
        });
        return response.data;
    },

    createNext4Weeks: async (fromWeekStart = null) => {
        const response = await apiClient.post('/timetable/weeks/create_next_4_weeks/', {
            from_week_start: fromWeekStart,
        });
        return response.data;
    },

    saveGrid: async (weekId, rows, cells) => {
        const response = await apiClient.post(`/timetable/weeks/${weekId}/save_grid/`, {
            rows,
            cells,
        });
        return response.data;
    },

    verifyWeek: async (weekId) => {
        const response = await apiClient.post(`/timetable/weeks/${weekId}/verify/`);
        return response.data;
    },

    publishWeek: async (weekId) => {
        const response = await apiClient.post(`/timetable/weeks/${weekId}/publish/`);
        return response.data;
    },

    revertToDraft: async (weekId, reason) => {
        const response = await apiClient.post(`/timetable/weeks/${weekId}/revert_to_draft/`, {
            reason,
        });
        return response.data;
    },

    getChangeLogs: async (weekId) => {
        const response = await apiClient.get(`/timetable/weeks/${weekId}/change_logs/`);
        return response.data;
    },

    // Session occurrences
    getSessions: async (params = {}) => {
        const response = await apiClient.get('/timetable/sessions/', { params });
        return response.data;
    },
};
