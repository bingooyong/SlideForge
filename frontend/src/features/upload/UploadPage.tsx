import { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";
import { FileUpload } from "./FileUpload";
import { PageSelector, PageThumbnail } from "./PageSelector";
import { TaskStatus, useTaskStore } from "../../stores/taskStore";
import { getSettings } from "../../stores/settingsStore";
import { useWebSocket, WebSocketProgressMessage } from "../../hooks/useWebSocket";
import { ProgressBar } from "../../components/ProgressBar";
import { ExportButton } from "../../components/ExportButton";
import { HomeGuidance } from "../../components/HomeGuidance";

interface UploadResponse {
  taskId: string;
  filename: string;
  pageCount: number;
  status: TaskStatus["status"];
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [mode, setMode] = useState<"lite" | "standard">("standard");
  const [aspectRatio, setAspectRatio] = useState<"16:9" | "9:16" | "4:3">("16:9");
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const s = getSettings();
    setApiKey(s.geminiApiKey);
    setMode(s.defaultMode);
    setAspectRatio(s.defaultAspectRatio);
  }, []);

  const [selectedPages, setSelectedPages] = useState<number[]>([]);
  const [pageCount, setPageCount] = useState(0);

  const { tasks, upsertTask, updateTask } = useTaskStore();
  const currentTask = taskId ? tasks[taskId] : undefined;

  const isTaskActive = useMemo(
    () => Boolean(taskId && currentTask && currentTask.status !== "completed" && currentTask.status !== "failed"),
    [taskId, currentTask],
  );

  const handleProgressMessage = useCallback(
    (message: WebSocketProgressMessage) => {
      const nextStatus: TaskStatus["status"] =
        message.status ?? (message.stage === "completed" ? "completed" : "processing");
      updateTask(message.taskId, {
        status: nextStatus,
        progress: message.progress,
        currentPage: message.pageIndex,
        totalPages: message.totalPages,
        stage: message.stage,
        ...(message.failedPages && message.failedPages.length > 0
          ? { failedPages: message.failedPages }
          : {}),
      });
      setPageCount(message.totalPages);
      if (nextStatus === "failed") {
        setError("任务处理失败，请检查 GEMINI_API_KEY 或稍后重试。");
      }
    },
    [updateTask],
  );

  const { connectionState, lastMessage, reconnectAttempt } = useWebSocket({
    taskId,
    enabled: isTaskActive,
    onProgressMessage: handleProgressMessage,
  });

  const handleFileSelected = (selected: File) => {
    setFile(selected);
    setError(null);
    setSelectedPages([]);
    setTaskId(null);
    setPageCount(0);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("请先选择文件。");
      return;
    }

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("mode", mode);
    formData.append("aspectRatio", aspectRatio);
    if (apiKey) {
      formData.append("apiKey", apiKey);
    }

    try {
      const response = await axios.post<UploadResponse>("/api/v1/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      const data = response.data;
      setTaskId(data.taskId);
      setPageCount(data.pageCount);

      const initialTask: TaskStatus = {
        taskId: data.taskId,
        filename: data.filename,
        status: data.status,
        progress: 0,
        currentPage: 0,
        totalPages: data.pageCount,
        stage: "uploading",
        failedPages: [],
      };
      upsertTask(initialTask);
    } catch (err) {
      console.error("上传失败", err);
      setError("上传失败，请稍后重试。");
    } finally {
      setIsUploading(false);
    }
  };

  const pageThumbnails: PageThumbnail[] = useMemo(() => {
    if (pageCount <= 0 || !taskId) return [];
    return Array.from({ length: pageCount }, (_, index) => ({
      pageIndex: index,
      imageUrl: `/api/v1/tasks/${taskId}/preview/${index}`,
    }));
  }, [pageCount, taskId]);

  return (
    <div className="upload-page-wrap">
      <HomeGuidance />
      <div className="upload-page">
      <section className="upload-page__panel upload-page__panel--primary">
        <header className="upload-page__section-header">
          <h2>上传与转换</h2>
          <p>上传 PDF 或图片，选择转换参数，系统将自动生成可导出的 PPTX。</p>
        </header>

        <FileUpload onFileSelected={handleFileSelected} disabled={isUploading} />

        {file ? (
          <p className="upload-page__file-meta" role="status">
            已选择：{file.name}（{formatFileSize(file.size)}）
          </p>
        ) : null}

        <div className="upload-page__options">
          <label className="upload-page__field">
            <span>转换模式</span>
            <select
              value={mode}
              onChange={(event) => setMode(event.target.value as "lite" | "standard")}
              disabled={isUploading}
            >
              <option value="lite">Lite（快速，无样式）</option>
              <option value="standard">Standard（完整样式）</option>
            </select>
          </label>

          <label className="upload-page__field">
            <span>画面比例</span>
            <select
              value={aspectRatio}
              onChange={(event) => setAspectRatio(event.target.value as "16:9" | "9:16" | "4:3")}
              disabled={isUploading}
            >
              <option value="16:9">16:9</option>
              <option value="9:16">9:16</option>
              <option value="4:3">4:3</option>
            </select>
          </label>

          <label className="upload-page__field upload-page__field--full">
            <span>Gemini API Key（可选）</span>
            <input
              type="password"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              placeholder="仅在本地环境输入，不会持久化"
              disabled={isUploading}
            />
          </label>
        </div>

        <button
          type="button"
          className="upload-page__submit"
          onClick={handleUpload}
          disabled={isUploading || !file}
        >
          {isUploading ? "上传中..." : "开始上传"}
        </button>

        {currentTask ? (
          <div className="upload-page__status">
            <p>任务 ID：{currentTask.taskId}</p>
            <ProgressBar
              task={currentTask}
              connectionState={connectionState}
              reconnectAttempt={reconnectAttempt}
              message={lastMessage?.message}
            />
          </div>
        ) : null}

        <ExportButton taskId={taskId} disabled={!currentTask || currentTask.status !== "completed"} />

        {currentTask?.status === "completed" &&
        currentTask.failedPages &&
        currentTask.failedPages.length > 0 ? (
          <p className="upload-page__degradation" role="status">
            第 {currentTask.failedPages.map((i) => i + 1).join("、")} 页为降级（原图占位），建议在
            PowerPoint 中检查并酌情调整。
          </p>
        ) : null}

        {error ? <p className="upload-page__error">{error}</p> : null}
      </section>

      <section className="upload-page__panel upload-page__preview">
        <header className="upload-page__section-header">
          <h2>页面选择</h2>
          <p>可按页预览并选择需要导出的页面。</p>
        </header>
        <PageSelector
          pages={pageThumbnails}
          selectedPages={selectedPages}
          onChangeSelectedPages={setSelectedPages}
        />
      </section>
      </div>
    </div>
  );
}
