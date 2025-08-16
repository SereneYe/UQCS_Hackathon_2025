import { apiClient } from "./api";

export type SignedUrl = {
  fileName: string;
  gcsFileName: string;
  url: string;
  method: "PUT";
  headers: Record<string, string>;
  expiresAt: string;
  bucket: string;
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

export async function getSignedUploadUrls(files: File[]): Promise<{ urls: SignedUrl[] }> {
  const userId = getCurrentUserIdFromStorage();
  if (!userId) {
    throw new Error("No user id in local storage. Please create an account or sign in first.");
  }

  const payload = {
    userId,
    files: files.map((f) => ({
      fileName: f.name,
      size: f.size,
      contentType: f.type || "application/octet-stream",
    })),
  };

  return apiClient.post<{ urls: SignedUrl[] }>("/storage/upload-urls", payload);
}

export async function uploadFileToSignedUrl(url: string, file: File, headers: Record<string, string>) {
  const res = await fetch(url, {
    method: "PUT",
    headers: {
      ...(headers || {}),
    },
    body: file,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`GCS upload failed: ${res.status} ${text}`);
  }
}