import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { consultsAPI } from '../api';

export const useConsults = (params = {}) => {
    return useQuery({
        queryKey: ['consults', params],
        queryFn: () => consultsAPI.getConsults(params),
    });
};

export const useConsult = (id) => {
    return useQuery({
        queryKey: ['consult', id],
        queryFn: () => consultsAPI.getConsult(id),
        enabled: !!id,
    });
};

export const useCreateConsult = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: consultsAPI.createConsult,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['consults'] });
        },
    });
};

export const useAcknowledgeConsult = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: consultsAPI.acknowledgeConsult,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['consults'] });
        },
    });
};

export const useAssignConsult = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, assignedTo }) => consultsAPI.assignConsult(id, assignedTo),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['consults'] });
        },
    });
};

export const useAddNote = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, noteData }) => consultsAPI.addNote(id, noteData),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['consult', variables.id] });
            queryClient.invalidateQueries({ queryKey: ['consults'] });
        },
    });
};

export const useCompleteConsult = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: consultsAPI.completeConsult,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['consults'] });
        },
    });
};

export const useDashboardStats = () => {
    return useQuery({
        queryKey: ['dashboard-stats'],
        queryFn: consultsAPI.getDashboardStats,
    });
};
