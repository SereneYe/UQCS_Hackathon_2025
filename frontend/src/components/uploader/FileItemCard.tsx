import { useEffect } from "react";
import type { PreparedFile } from "../../types/upload";
import PDFThumbnail from "./PDFThumbnail";

interface Props {
  item: PreparedFile;
  onRemove: (id: string) => void | Promise<void>;
}

export default function FileItemCard({ item, onRemove }: Props) {
  const isImage = item.kind === "image";
  const isPDF = item.kind === "pdf";

  useEffect(() => {
    return () => {
      if (item.previewUrl) URL.revokeObjectURL(item.previewUrl);
    };
  }, [item.previewUrl]);

  return (
    <div className="relative rounded-lg border border-gray-700 bg-arcade-terminal overflow-hidden">
      <div className="h-28 w-full bg-black/20 flex items-center justify-center">
        {isImage && item.previewUrl ? (
          <img
            src={item.previewUrl}
            alt={item.name}
            className="h-full w-full object-cover"
          />
        ) : isPDF ? (
          <PDFThumbnail item={item} />
        ) : (
          <div className="text-sm text-gray-400 px-3 text-center">
            Cannot preview file type.
          </div>
        )}
      </div>

      <div className="px-3 py-2 text-xs text-gray-300 truncate">{item.name}</div>

      {item.status === "uploading" && (
        <div className="absolute inset-x-0 bottom-0 h-1 bg-arcade-purple/30">
          <div className="h-full bg-arcade-purple animate-pulse" style={{ width: "80%" }} />
        </div>
      )}

      {item.status === "error" && (
        <div className="px-3 pb-2 text-xs text-red-400">{item.errorMsg ?? "Failed to upload"}</div>
      )}

      <button
        type="button"
        aria-label="Delete"
        onClick={() => void onRemove(item.id)}
        className="absolute top-2 right-2 bg-black/60 hover:bg-black/80 text-white text-xs px-2 py-1 rounded"
      >
        Delete
      </button>
    </div>
  );
}