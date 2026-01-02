import apiClient from './client';

// Fee Types
export const getFeeTypes = () => apiClient.get('/finance/fee-types/');
export const createFeeType = (data) => apiClient.post('/finance/fee-types/', data);
export const updateFeeType = (id, data) => apiClient.patch(`/finance/fee-types/${id}/`, data);
export const deleteFeeType = (id) => apiClient.delete(`/finance/fee-types/${id}/`);

// Fee Plans
export const getFeePlans = (params) => apiClient.get('/finance/fee-plans/', { params });
export const createFeePlan = (data) => apiClient.post('/finance/fee-plans/', data);
export const updateFeePlan = (id, data) => apiClient.patch(`/finance/fee-plans/${id}/`, data);

// Vouchers
export const getVouchers = (params) => apiClient.get('/finance/vouchers/', { params });
export const getVoucher = (id) => apiClient.get(`/finance/vouchers/${id}/`);
export const generateVouchers = (data) => apiClient.post('/finance/vouchers/generate/', data);
export const cancelVoucher = (id, reason) => apiClient.post(`/finance/vouchers/${id}/cancel/`, { reason });
export const downloadVoucherPDF = (id) => apiClient.get(`/finance/vouchers/${id}/pdf/`, { responseType: 'blob' });

// Payments
export const getPayments = (params) => apiClient.get('/finance/payments/', { params });
export const getPayment = (id) => apiClient.get(`/finance/payments/${id}/`);
export const createPayment = (data) => apiClient.post('/finance/payments/', data);
export const verifyPayment = (id) => apiClient.post(`/finance/payments/${id}/verify/`);
export const downloadReceiptPDF = (id) => apiClient.get(`/finance/payments/${id}/pdf/`, { responseType: 'blob' });

// Student Summary
export const getStudentFinanceSummary = (studentId, params) => 
  apiClient.get(`/finance/students/${studentId}/summary/`, { params });

// Reports
export const getDefaulters = (params) => apiClient.get('/finance/reports/defaulters/', { params });
export const getCollectionReport = (params) => apiClient.get('/finance/reports/collection/', { params });

// Ledger
export const getLedgerEntries = (params) => apiClient.get('/finance/ledger/', { params });
