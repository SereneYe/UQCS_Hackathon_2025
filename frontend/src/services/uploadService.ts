// frontend/src/services/uploadService.ts
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

export async function getSignedUploadUrls(files: File[]): Promise<{ urls: SignedUrl[] }> {
  const payload = files.map((f) => ({
    fileName: f.name,
    size: f.size,
    contentType: f.type || "application/octet-stream",
  }));
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