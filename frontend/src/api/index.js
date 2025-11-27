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

    // Consult management
    reassignConsult: async (id, data) => {
        const response = await apiClient.post(`/admin/consults/${id}/reassign/`, data);
        return response.data;
    },

    forceCloseConsult: async (id, data) => {
        const response = await apiClient.post(`/admin/consults/${id}/force-close/`, data);
        return response.data;
    },
};
