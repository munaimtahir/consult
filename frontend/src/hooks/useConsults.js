import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { consultsAPI } from '../api';

/**
 * A custom hook for fetching a list of consults.
 *
 * @param {object} params - The query parameters for filtering the consults.
 * @returns {import('@tanstack/react-query').UseQueryResult} The result of
 *   the query.
 */
export const useConsults = (params = {}) => {
    return useQuery({
        queryKey: ['consults', params],
        queryFn: () => consultsAPI.getConsults(params),
    });
};

/**
 * A custom hook for fetching a single consult by its ID.
 *
 * @param {string} id - The ID of the consult to fetch.
 * @returns {import('@tanstack/react-query').UseQueryResult} The result of
 *   the query.
 */
export const useConsult = (id) => {
    return useQuery({
        queryKey: ['consult', id],
        queryFn: () => consultsAPI.getConsult(id),
        enabled: !!id,
    });
};

/**
 * A custom hook for creating a new consult.
 *
 * @returns {import('@tanstack/react-query').UseMutationResult} The result of
 *   the mutation.
 */
export const useCreateConsult = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: consultsAPI.createConsult,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['consults'] });
        },
    });
};

/**
 * A custom hook for acknowledging a consult.
 *
 * @returns {import('@tanstack/react-query').UseMutationResult} The result of
 *   the mutation.
 */
export const useAcknowledgeConsult = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: consultsAPI.acknowledgeConsult,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['consults'] });
        },
    });
};

/**
 * A custom hook for assigning a consult to a user.
 *
 * @returns {import('@tanstack/react-query').UseMutationResult} The result of
 *   the mutation.
 */
export const useAssignConsult = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, assignedTo }) => consultsAPI.assignConsult(id, assignedTo),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['consults'] });
        },
    });
};

/**
 * A custom hook for adding a note to a consult.
 *
 * @returns {import('@tanstack/react-query').UseMutationResult} The result of
 *   the mutation.
 */
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

/**
 * A custom hook for completing a consult.
 *
 * @returns {import('@tanstack/react-query').UseMutationResult} The result of
 *   the mutation.
 */
export const useCompleteConsult = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: consultsAPI.completeConsult,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['consults'] });
        },
    });
};

/**
 * A custom hook for fetching dashboard statistics.
 *
 * @returns {import('@tanstack/react-query').UseQueryResult} The result of
 *   the query.
 */
export const useDashboardStats = () => {
    return useQuery({
        queryKey: ['dashboard-stats'],
        queryFn: consultsAPI.getDashboardStats,
    });
};
