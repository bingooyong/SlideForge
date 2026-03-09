import axios from "axios";
import { useState } from "react";

interface ExportButtonProps {
  taskId: string | null;
  disabled?: boolean;
}

function resolveFilename(taskId: string, disposition: string | undefined): string {
  if (!disposition) return `task-${taskId}.pptx`;
  const match = disposition.match(/filename="?([^"]+)"?/i);
  return match?.[1] ?? `task-${taskId}.pptx`;
}

export function ExportButton({ taskId, disabled = false }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    if (!taskId || disabled || isExporting) return;

    setIsExporting(true);
    setError(null);

    try {
      const response = await axios.get(`/api/v1/export/${taskId}`, { responseType: "blob" });
      const filename = resolveFilename(taskId, response.headers["content-disposition"]);
      const blobUrl = window.URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (err: unknown) {
      console.error("导出失败", err);
      const status = axios.isAxiosError(err) ? err.response?.status : undefined;
      const detail = axios.isAxiosError(err) && err.response?.data?.detail;
      if (status === 202) {
        setError("任务尚未完成，请稍候再试。");
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("导出失败，请稍后重试。");
      }
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="export-button">
      <button type="button" onClick={handleExport} disabled={!taskId || disabled || isExporting}>
        {isExporting ? "导出中..." : "导出 PPTX"}
      </button>
      {error ? <p className="export-button__error">{error}</p> : null}
    </div>
  );
}
