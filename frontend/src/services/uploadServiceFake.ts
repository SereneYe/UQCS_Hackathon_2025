export type FakeUploadUrl = { fileName: string; url: string };

export async function getUploadUrlFake(files: File[]): Promise<{ urls: FakeUploadUrl[] }> {
  // TODO: Replace with GCP signed URL generation
  // This should call GCP Storage API to get signed URLs for direct upload
  await new Promise((r) => setTimeout(r, 400));
  return {
    urls: files.map((f, i) => ({
      fileName: f.name,
      url: `https://fake-upload.local/upload/${encodeURIComponent(f.name)}?i=${i}`,
    })),
  };
}

export async function uploadFileFake(url: string, file: File): Promise<{ ok: boolean }> {
  // TODO: Replace with actual GCP direct upload using signed URL
  // This should perform PUT request to the signed URL with the file data
  await new Promise((r) => setTimeout(r, 500 + Math.random() * 800));
  const ok = Math.random() > 0.1; // 90% success rate
  if (!ok) throw new Error("Upload failed, please try again");
  return { ok: true };
}

export async function deleteFileFake(idOrName: string): Promise<void> {
  // TODO: Replace with GCP file deletion
  // This should call GCP Storage API to delete the file from the bucket
  await new Promise((r) => setTimeout(r, 200));
  return;
}

// TODO: Replace all above functions with actual GCP integration:
// - getUploadUrlFake -> Get signed URLs from GCP Storage
// - uploadFileFake -> Direct PUT upload to signed URL
// - deleteFileFake -> Delete file from GCP Storage bucket