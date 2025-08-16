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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.all });
    },
  });
};