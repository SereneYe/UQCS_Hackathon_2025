import { useState, useEffect } from 'react';
import type { PreparedFile } from '../../types/upload';

interface Props {
  item: PreparedFile;
}

export default function PDFThumbnail({ item }: Props) {
  const [fileInfo, setFileInfo] = useState<{
    pages?: number;
    size: string;
  }>({ size: '' });

  useEffect(() => {
    const formatFileSize = (bytes: number): string => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // For now, just format the file size
    // In the future, we could use PDF.js to read actual page count
    setFileInfo({
      size: formatFileSize(item.size)
    });
  }, [item.size]);

  return (
    <div className="flex flex-col items-center justify-center h-full text-gray-200 px-3 py-2">
      {/* PDF Icon */}
      <div className="text-3xl mb-2">📄</div>
      
      {/* File info */}
      <div className="text-center">
        <div className="text-xs font-medium text-gray-100 mb-1">PDF Document</div>
        <div className="text-xs text-gray-400">{fileInfo.size}</div>
        {fileInfo.pages && (
          <div className="text-xs text-gray-400">{fileInfo.pages} pages</div>
        )}
      </div>

      {/* Background pattern for visual appeal */}
      <div className="absolute inset-0 opacity-5">
        <div className="w-full h-full" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='3' cy='3' r='3'/%3E%3Ccircle cx='13' cy='13' r='3'/%3E%3C/g%3E%3C/svg%3E")`,
          backgroundSize: '20px 20px'
        }} />
      </div>
    </div>
  );
}