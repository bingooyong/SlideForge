import { useCallback, useRef, useState } from "react";

type SupportedFile = File & {
  type: string;
};

const ACCEPTED_MIME_TYPES = [
  "application/pdf",
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/bmp",
];

const ACCEPT_ATTR = ".pdf,image/*";

export interface FileUploadProps {
  onFileSelected: (file: SupportedFile) => void;
  disabled?: boolean;
}

export function FileUpload({ onFileSelected, disabled }: FileUploadProps) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const validateFile = useCallback((file: File | null): SupportedFile | null => {
    if (!file) {
      return null;
    }
    if (!ACCEPTED_MIME_TYPES.includes(file.type)) {
      setError("仅支持 PDF 与图片文件（JPG/PNG/WebP/BMP）。");
      return null;
    }
    setError(null);
    return file as SupportedFile;
  }, []);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files || files.length === 0) return;
      const file = validateFile(files[0]);
      if (file) {
        onFileSelected(file);
      }
    },
    [onFileSelected, validateFile],
  );

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled) return;
    handleFiles(event.target.files);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (disabled) return;
    setDragOver(false);
    handleFiles(event.dataTransfer.files);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (disabled) return;
    setDragOver(true);
  };

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (disabled) return;
    setDragOver(false);
  };

  const handleClick = () => {
    if (disabled) return;
    inputRef.current?.click();
  };

  return (
    <div>
      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        role="button"
        aria-disabled={disabled}
        tabIndex={disabled ? -1 : 0}
        className={`file-upload-dropzone${dragOver ? " file-upload-dropzone--drag-over" : ""}${
          disabled ? " file-upload-dropzone--disabled" : ""
        }`}
      >
        <p>拖拽 PDF 或图片到此处，或点击选择文件</p>
        <p className="file-upload-hint">支持：PDF, JPG, PNG, WebP, BMP</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT_ATTR}
        style={{ display: "none" }}
        onChange={handleInputChange}
        disabled={disabled}
      />
      {error ? <p className="file-upload-error">{error}</p> : null}
    </div>
  );
}

