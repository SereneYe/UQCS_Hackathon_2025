import { ENV } from '@/config/environment';

export type VideoSession = {
  id: number;
  user_id: number;
  session_name?: string;
  description?: string;
  status: string;
  created_at: string;
  output_video_path?: string;
  // Other fields can be extended as needed
};

function getCurrentUserIdFromStorage(): number | null {
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