import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';

export interface Video {
  id: number;
  user_email: string;
  video_task_id: string;
  veo_task_id: string;
  status: string;
}

export interface VideoCreate {
  user_email: string;
  video_task_id: string;
  veo_task_id: string;
  status: string;
}

export interface VideoUpdate {
  user_email?: string;
  video_task_id?: string;
  veo_task_id?: string;
  status?: string;
}

// Query Keys
export const videoKeys = {
  all: ['videos'] as const,
  lists: () => [...videoKeys.all, 'list'] as const,
  list: (filters: Record<string, unknown>) => [...videoKeys.lists(), { filters }] as const,
  details: () => [...videoKeys.all, 'detail'] as const,
  detail: (id: number) => [...videoKeys.details(), id] as const,
  byUser: (email: string) => [...videoKeys.all, 'user', email] as const,
  byTaskId: (taskId: string) => [...videoKeys.all, 'taskId', taskId] as const,
} as const;

// Hooks
export const useGetVideos = (skip = 0, limit = 100) => {
  return useQuery({
    queryKey: videoKeys.list({ skip, limit }),
    queryFn: () => apiClient.get<Video[]>(`/videos/?skip=${skip}&limit=${limit}`),
  });
};

export const useGetVideo = (videoId: number) => {
  return useQuery({
    queryKey: videoKeys.detail(videoId),
    queryFn: () => apiClient.get<Video>(`/videos/${videoId}`),
    enabled: !!videoId,
  });
};

export const useGetVideosByUserEmail = (userEmail: string) => {
  return useQuery({
    queryKey: videoKeys.byUser(userEmail),
    queryFn: () => apiClient.get<Video[]>(`/videos/user/${userEmail}`),
    enabled: !!userEmail,
  });
};

export const useGetVideoByTaskId = (taskId: string) => {
  return useQuery({
    queryKey: videoKeys.byTaskId(taskId),
    queryFn: () => apiClient.get<Video>(`/videos/task/${taskId}`),
    enabled: !!taskId,
  });
};

export const useCreateVideo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (videoData: VideoCreate) => 
      apiClient.post<Video>('/videos/', videoData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: videoKeys.all });
    },
  });
};

export const useUpdateVideo = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: VideoUpdate }) => 
      apiClient.put<Video>(`/videos/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: videoKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: videoKeys.lists() });
    },
  });
};