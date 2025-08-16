export type FileKind = "image" | "pdf" | "other";

export interface PreparedFile {
  id: string;
  file: File;
  kind: FileKind;
  name: string;
  size: number;
  previewUrl?: string;
  status: "pending" | "uploading" | "ready" | "error";
  errorMsg?: string;
}

export const ACCEPT_TYPES = [
  "image/png",
  "image/jpeg",
  "image/webp",
  "image/gif",
  "application/pdf",
] as const;

export const MB = 1024 * 1024;