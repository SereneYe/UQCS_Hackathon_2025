import { useCallback, useMemo, useState, useEffect } from "react";
import { uploadFileToBackend, deleteFileFromBackend, getFilesByVideoSession, type BackendFile } from "../../services/fileUploadService";
import { getCurrentSessionIdFromStorage } from "../../services/videoSessionService";
import FileItemCard from "./FileItemCard";
import type { PreparedFile, FileKind } from "../../types/upload";

const IMAGE_TYPES = [
  "image/png",
  "image/jpeg",
  "image/webp",
  "image/gif",
] as const;

const MB = 1024 * 1024;

interface Props {
	maxFiles?: number;
	maxFileSizeMB?: number;
	onChange?: (files: PreparedFile[]) => void;
}

export default function ImageUploader({
									 maxFiles = 10,
									 maxFileSizeMB = 10,
									 onChange,
								 }: Props) {
	const [items, setItems] = useState<PreparedFile[]>([]);
	const [isDragging, setIsDragging] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [isLoadingExisting, setIsLoadingExisting] = useState(false);
	const isUploading = items.some((i) => i.status === "uploading");
	
	const acceptSet = useMemo(() => new Set(IMAGE_TYPES), []);
	
	// Load existing image files for current session on mount
	useEffect(() => {
		const loadExistingFiles = async () => {
			const sessionId = getCurrentSessionIdFromStorage();
			if (!sessionId) return;
			
			try {
				setIsLoadingExisting(true);
				const backendFiles = await getFilesByVideoSession(sessionId);
				// Filter only image files and take only the first one
				const imageFiles = backendFiles.filter(file => file.category === "image");
				const preparedFiles = imageFiles.length > 0 ? [convertBackendFileToPreparedFile(imageFiles[0])] : [];
				setItems(preparedFiles);
				// Only call onChange if we actually have files to avoid triggering collapse
				if (preparedFiles.length > 0) {
					onChange?.(preparedFiles);
				}
			} catch (error) {
				console.error("Failed to load existing image files:", error);
				setError("Failed to load existing image files");
			} finally {
				setIsLoadingExisting(false);
			}
		};
		
		loadExistingFiles();
	}, []);
	
	const classifyKind = (type: string): FileKind => {
		if (type.startsWith("image/")) return "image";
		return "other";
	};
	
	const convertBackendFileToPreparedFile = (backendFile: BackendFile): PreparedFile => {
		return {
			id: `backend-${backendFile.id}`,
			file: new File([], backendFile.original_filename, { type: backendFile.content_type }),
			kind: classifyKind(backendFile.content_type),
			name: backendFile.original_filename,
			size: backendFile.file_size,
			previewUrl: backendFile.public_url,
			status: "ready",
			backendId: backendFile.id,
		};
	};
	
	const validateFiles = (files: File[]): string | null => {
		if (!files.length) return null;
		if (items.length > 0) {
			return `Only one image is allowed. Please remove the current image first.`;
		}
		if (files.length > 1) {
			return `Only one image can be uploaded at a time.`;
		}
		const f = files[0];
		if (f.size > maxFileSizeMB * MB) {
			return `Image file is too big（Max ${maxFileSizeMB}MB）：${f.name}`;
		}
		if (!IMAGE_TYPES.includes(f.type as any)) {
			return `Not supported image type: ${f.name}. Supported: PNG, JPEG, WebP, GIF`;
		}
		return null;
	};
	
	const pickFiles = async (files: File[]) => {
		setError(null);
		const err = validateFiles(files);
		if (err) {
			setError(err);
			return;
		}
		
		// Create pending items with local preview for images
		const pending: PreparedFile[] = files.map((f) => ({
			id: `${f.name}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
			file: f,
			kind: classifyKind(f.type),
			name: f.name,
			size: f.size,
			previewUrl: URL.createObjectURL(f),
			status: "pending",
		}));
		
		setItems((prev) => {
			const next = [...prev, ...pending];
			onChange?.(next.filter((i) => i.status === "ready"));
			return next;
		});
		
		try {
			// Set to uploading status
			setItems((prev) => prev.map((i) => (pending.some((p) => p.id === i.id) ? {...i, status: "uploading"} : i)));
			
			// Upload each file to backend in parallel
			await Promise.all(
				pending.map(async (p) => {
					try {
						const sessionId = getCurrentSessionIdFromStorage();
						const uploadResult = await uploadFileToBackend(p.file, undefined, undefined, false, sessionId || undefined);
						setItems((prev) => {
							const next = prev.map((it) => (it.id === p.id ? {...it, status: "ready", backendId: uploadResult.id} : it));
							onChange?.(next.filter((i) => i.status === "ready"));
							return next;
						});
					} catch (e: unknown) {
						const errorMsg = e instanceof Error ? e.message : "Failed to upload image";
						console.error("Upload failed:", errorMsg);
						setItems((prev) =>
							prev.map((it) =>
								it.id === p.id ? {...it, status: "error", errorMsg} : it
							)
						);
					}
				})
			);
		} catch (e: unknown) {
			const errorMsg = e instanceof Error ? e.message : "Failed to upload image files. Please try again later.";
			setError(errorMsg);
			// Set all pending items to error
			setItems((prev) =>
				prev.map((it) =>
					pending.some((p) => p.id === it.id) ? {...it, status: "error", errorMsg: "Failed to initialize"} : it
				)
			);
		}
	};
	
	const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const files = e.target.files ? Array.from(e.target.files) : [];
		void pickFiles(files);
		// Clear input to allow selecting same file again
		e.currentTarget.value = "";
	};
	
	const onDrop = useCallback(
		(e: React.DragEvent<HTMLDivElement>) => {
			e.preventDefault();
			e.stopPropagation();
			setIsDragging(false);
			const files = Array.from(e.dataTransfer.files);
			void pickFiles(files);
		},
		[pickFiles]
	);
	
	const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		setIsDragging(true);
	};
	
	const onDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		setIsDragging(false);
	};
	
	const removeItem = async (id: string) => {
		const item = items.find(i => i.id === id);
		
		// If file was successfully uploaded, delete from backend
		if (item && item.backendId && item.status === "ready") {
			try {
				await deleteFileFromBackend(item.backendId);
			} catch (error) {
				console.error("Failed to delete image from backend:", error);
				// Continue with local removal even if backend delete fails
			}
		}
		
		setItems((prev) => {
			const next = prev.filter((i) => i.id !== id);
			onChange?.(next.filter((i) => i.status === "ready"));
			return next;
		});
	};
	
	return (
		<div className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl p-6 border border-gray-800 shadow-xl">
			<div className="mb-4">
				<h3 className="text-white text-lg font-semibold mb-2 flex items-center justify-center">
					<span className="text-2xl mr-2">📸</span>
					Upload Image
				</h3>
				<p className="text-gray-400 text-sm text-center">Add an image to enhance your video content</p>
			</div>
			
			<div
				role="button"
				tabIndex={0}
				aria-label="Drag and drop images here or click to select images"
				onDrop={onDrop}
				onDragOver={onDragOver}
				onDragLeave={onDragLeave}
				className={[
					"w-full border rounded-lg p-4 text-white transition-colors",
					"bg-arcade-terminal border-gray-700",
					"focus:outline-none focus:ring-2 focus:ring-arcade-purple",
					isDragging ? "border-arcade-purple/60 bg-arcade-terminal/60" : "",
				].join(" ")}
			>
				<div className="flex flex-col items-center justify-center text-center py-8">
					<div className="text-gray-300 text-sm mb-4">
						Drag and drop an image here or click to select. Up to {maxFileSizeMB}MB.
					</div>
					<label className="inline-flex items-center">
						<input
							type="file"
							accept={IMAGE_TYPES.join(",")}
							onChange={onInputChange}
							className="hidden"
							aria-label="Choose image file"
						/>
						<span
							className="cursor-pointer bg-arcade-purple hover:bg-opacity-90 text-white rounded px-4 py-2 text-sm font-medium">
              Choose Image
            </span>
					</label>
				</div>
			</div>
			
			{error && <div className="mt-2 text-sm text-red-400">{error}</div>}
			
			{items.length > 0 && (
				<div className="mt-6 flex justify-center">
					<div className="w-64 h-48">
						<FileItemCard key={items[0].id} item={items[0]} onRemove={removeItem}/>
					</div>
				</div>
			)}
			
			{isUploading && (
				<div className="mt-3 text-xs text-gray-400 text-center">Uploading image...</div>
			)}
			
			{isLoadingExisting && (
				<div className="mt-3 text-xs text-gray-400 text-center">Loading existing image...</div>
			)}
		</div>
	);
}