import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';

export interface User {
  id: number;
  email: string;
}

export interface UserCreate {
  email: string;
}

// Query Keys
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: Record<string, unknown>) => [...userKeys.lists(), { filters }] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: number) => [...userKeys.details(), id] as const,
} as const;

// Hooks
export const useGetUsers = (skip = 0, limit = 100) => {
  return useQuery({
    queryKey: userKeys.list({ skip, limit }),
    queryFn: () => apiClient.get<User[]>(`/users/?skip=${skip}&limit=${limit}`),
  });
};

export const useGetUser = (userId: number) => {
  return useQuery({
    queryKey: userKeys.detail(userId),
    queryFn: () => apiClient.get<User>(`/users/${userId}`),
    enabled: !!userId,
  });
};

export const useGetUserByEmail = (email: string) => {
  return useQuery({
    queryKey: ['users', 'email', email],
    queryFn: () => apiClient.get<User>(`/users/email/${email}`),
    enabled: !!email,
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: UserCreate) =>
      apiClient.post<User>('/users/', userData),
    onSuccess: (data) => {
      if (data?.id && data?.email) {
        try {
          localStorage.setItem('currentUserId', String(data.id));
          localStorage.setItem('currentUserEmail', data.email);
        } catch {
          // ignore the error
        }
      }
      
      queryClient.invalidateQueries({ queryKey: userKeys.all });
    },
  });
};

// Optional: If caller wants "explicitly wait for user + session both created before continuing (like navigation)",
// recommend exporting a convenience Hook that uses mutateAsync directly to ensure sequence.
export const useCreateUserAndBootstrapSession = () => {
  const mutation = useCreateUser();

  // Return a convenient mutateAsync wrapper to ensure caller awaits completion before navigation
  const createAndEnsureSession = async (payload: UserCreate) => {
    // mutateAsync will wait for onSuccess internal async logic to complete
    const result = await mutation.mutateAsync(payload);
    return result;
  };

  return { ...mutation, createAndEnsureSession };
};

export const getCurrentUserId = (): number | null => {
  try {
    const raw = localStorage.getItem('currentUserId');
    if (!raw) return null;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
  } catch {
    return null;
  }
};