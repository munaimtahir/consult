import apiClient from './client';

export const authAPI = {
    login: async (email, password) => {
        const response = await apiClient.post('/api/v1/auth/token/', {
            email,
            password,
        });
        return response.data;
    },

    getCurrentUser: async () => {
        const response = await apiClient.get('/api/v1/auth/users/me/');
        return response.data;
    },

    refreshToken: async (refreshToken) => {
        const response = await apiClient.post('/api/v1/auth/token/refresh/', {
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
