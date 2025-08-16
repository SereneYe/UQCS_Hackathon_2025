import { useCallback, useMemo, useState } from "react";
import { uploadFileToBackend } from "../../services/fileUploadService";
import FileItemCard from "./FileItemCard";
import { ACCEPT_TYPES, MB, type PreparedFile, type FileKind } from "../../types/upload";

interface Props {
	maxFiles?: number;
	maxFileSizeMB?: number;
	accept?: readonly string[];
	onChange?: (files: PreparedFile[]) => void;
}

export default function FileUploader({
										 maxFiles = 10,
										 maxFileSizeMB = 10,
										 accept = ACCEPT_TYPES,
										 onChange,
									 }: Props) {
	const [items, setItems] = useState<PreparedFile[]>([]);
	const [isDragging, setIsDragging] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const isUploading = items.some((i) => i.status === "uploading");
	
	const acceptSet = useMemo(() => new Set(accept), [accept]);
	
	const classifyKind = (type: string): FileKind => {
		if (type.startsWith("image/")) return "image";
		if (type === "application/pdf") return "pdf";
		return "other";
	};
	
	const validateFiles = (files: File[]): string | null => {
		if (!files.length) return null;
		if (items.length + files.length > maxFiles) {
			return `Only support no more than ${maxFiles} files.`;
		}
		for (const f of files) {
			if (f.size > maxFileSizeMB * MB) {
				return `File is too big（Max ${maxFileSizeMB}MB）：${f.name}`;
			}
			if (![...acceptSet].some((t) => f.type === t || (t.startsWith("image/") && f.type.startsWith("image/")))) {
				return `Not supported file type: ${f.name}`;
			}
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
			previewUrl: f.type.startsWith("image/") ? URL.createObjectURL(f) : undefined,
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
						const result = await uploadFileToBackend(p.file);
						setItems((prev) => {
							const next = prev.map((it) => (it.id === p.id ? {...it, status: "ready"} : it));
							onChange?.(next.filter((i) => i.status === "ready"));
							return next;
						});
					} catch (e: unknown) {
						const errorMsg = e instanceof Error ? e.message : "Failed to upload file";
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
			const errorMsg = e instanceof Error ? e.message : "Failed to upload files. Please try again later.";
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
	
	const removeItem = (id: string) => {
		setItems((prev) => {
			const next = prev.filter((i) => i.id !== id);
			onChange?.(next.filter((i) => i.status === "ready"));
			return next;
		});
	};
	
	return (
		<div className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl p-6 border border-gray-800 shadow-xl">
			<div
				role="button"
				tabIndex={0}
				aria-label="Drag and drop files here or click to select files"
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
				<div className="flex items-center justify-between">
					<div className="text-gray-300 text-sm">
						Drag and drop files here or click to select files. Max {maxFiles} files, up to {maxFileSizeMB}MB each.
					</div>
					<label className="inline-flex items-center">
						<input
							type="file"
							multiple
							accept={accept.join(",")}
							onChange={onInputChange}
							className="hidden"
							aria-label="Choose files"
						/>
						<span
							className="cursor-pointer bg-arcade-purple hover:bg-opacity-90 text-white rounded px-3 py-1.5 text-sm">
              Choose files
            </span>
					</label>
				</div>
			</div>
			
			{error && <div className="mt-2 text-sm text-red-400">{error}</div>}
			
			<div className="mt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
				{items.map((it) => (
					<FileItemCard key={it.id} item={it} onRemove={removeItem}/>
				))}
			</div>
			
			{isUploading && (
				<div className="mt-3 text-xs text-gray-400">Uploading...</div>
			)}
		</div>
	);
}