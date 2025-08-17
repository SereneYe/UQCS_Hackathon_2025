import { ENV } from '@/config/environment';
import { useQuery } from '@tanstack/react-query';

export type VideoSession = {
  id: number;
  user_id: number;
  session_name?: string;
  user_prompt?: string;
  category?: string;
  description?: string;
  status: string;
  total_files: number;
  processed_files: number;
  output_video_path?: string;
  video_url?: string;
  created_at: string;
  updated_at?: string;
};

export type VideoSessionList = {
  sessions: VideoSession[];
  total: number;
  page: number;
  per_page: number;
};

export function getCurrentUserIdFromStorage(): number | null {
  try {
    const raw = localStorage.getItem("currentUserId");
    if (!raw) return null;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
  } catch {
    return null;
  }
}

export async function createVideoSessionForCurrentUser(opts?: {
  sessionName?: string;
  description?: string;
}): Promise<VideoSession> {
  const userId = getCurrentUserIdFromStorage();
  if (!userId) {
    throw new Error("No user id in local storage. Please create an account or sign in first.");
  }

  const form = new FormData();
  form.append("user_id", String(userId));
  if (opts?.sessionName) form.append("session_name", opts.sessionName);
  if (opts?.description) form.append("description", opts.description);

  const res = await fetch(`${ENV.API_BASE_URL}/video-sessions/`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Create video session failed: ${res.status} ${text}`);
  }

  const data = (await res.json()) as VideoSession;

  if (!data?.id) {
    throw new Error("Create video session succeeded but response has no id.");
  }

  try {
    localStorage.setItem("currentSessionId", String(data.id));
  } catch {
    // Ignore localStorage write exceptions (e.g., privacy mode)
  }

  return data;
}

// Fetch user video sessions
export async function fetchUserVideoSessions(userId: number, skip: number = 0, limit: number = 50): Promise<VideoSessionList> {
  const res = await fetch(`${ENV.API_BASE_URL}/video-sessions/?user_id=${userId}&skip=${skip}&limit=${limit}`, {
    method: "GET",
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Failed to fetch video sessions: ${res.status} ${text}`);
  }

  return (await res.json()) as VideoSessionList;
}

// React Query hook for fetching user video sessions
export function useGetVideoSessions(userId?: number | null) {
  return useQuery({
    queryKey: ['videoSessions', 'user', userId],
    queryFn: () => {
      if (!userId) throw new Error("User ID is required");
      return fetchUserVideoSessions(userId);
    },
    enabled: !!userId,
  });
}

// Utility function to get current session ID from localStorage
export function getCurrentSessionIdFromStorage(): number | null {
  try {
    const raw = localStorage.getItem("currentSessionId");
    if (!raw) return null;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
  } catch {
    return null;
  }
}