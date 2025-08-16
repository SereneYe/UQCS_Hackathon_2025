// File upload service using backend endpoints directly

export type FileUploadResponse = {
  id: number;
  original_filename: string;
  gcs_filename: string;
  file_size: number;
  content_type: string;
  category: "image" | "pdf" | "audio" | "video" | "other";
  status: "uploading" | "completed" | "failed" | "deleted";
  public_url?: string;
  upload_url?: string;
  message: string;
};

function getCurrentUserEmailFromStorage(): string | null {
  try {
    const userEmail = localStorage.getItem("currentUserEmail");
    return userEmail;
  } catch {
    return null;
  }
}

export async function uploadFileToBackend(
  file: File,
  description?: string,
  tags?: string,
  isPublic: boolean = false,
  videoSessionId?: number
): Promise<FileUploadResponse> {
  const userEmail = getCurrentUserEmailFromStorage();
  
  // Create FormData for multipart/form-data upload
  const formData = new FormData();
  formData.append("file", file);
  
  if (userEmail) {
    formData.append("user_email", userEmail);
  }
  if (videoSessionId) {
    formData.append("video_session_id", videoSessionId.toString());
  }
  if (description) {
    formData.append("description", description);
  }
  if (tags) {
    formData.append("tags", tags);
  }
  formData.append("is_public", isPublic.toString());

  try {
    const response = await fetch("http://localhost:8000/files/upload", {
      method: "POST",
      body: formData,
      // Don't set Content-Type header - let browser set it with boundary for FormData
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "");
      throw new Error(`Upload failed: ${response.status} ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("File upload error:", error);
    throw error;
  }
}

export async function uploadMultipleFiles(
  files: File[],
  userEmail?: string,
  videoSessionId?: number
): Promise<{
  message: string;
  files: Array<{
    id: number;
    filename: string;
    size: number;
    status: string;
  }>;
}> {
  const formData = new FormData();
  
  // Append all files
  files.forEach(file => {
    formData.append("files", file);
  });
  
  if (userEmail) {
    formData.append("user_email", userEmail);
  }
  
  if (videoSessionId) {
    formData.append("video_session_id", videoSessionId.toString());
  }

  try {
    const response = await fetch("http://localhost:8000/files/upload-multiple", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "");
      throw new Error(`Multi-upload failed: ${response.status} ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Multiple file upload error:", error);
    throw error;
  }
}

// Backward compatibility: emulate the old signed URL structure for FileUploader
export async function getUploadUrlsCompat(files: File[]): Promise<{ urls: Array<{ url: string; headers?: Record<string, string> }> }> {
  // This function provides compatibility with the existing FileUploader
  // It doesn't actually get URLs but prepares for direct backend upload
  return {
    urls: files.map(() => ({
      url: "http://localhost:8000/files/upload", // Our backend endpoint
      headers: {}
    }))
  };
}

export async function uploadFileToBackendCompat(url: string, file: File, headers: Record<string, string>, videoSessionId?: number) {
  // Compatibility function for existing FileUploader
  return uploadFileToBackend(file, undefined, undefined, false, videoSessionId);
}