import { TaskStatus } from "../stores/taskStore";

interface ProgressBarProps {
  task: TaskStatus;
  connectionState: "idle" | "connecting" | "connected" | "reconnecting" | "disconnected" | "error";
  reconnectAttempt: number;
  message?: string;
}

const STAGE_LABELS: Record<TaskStatus["stage"], string> = {
  uploading: "上传中",
  processing: "处理中",
  synthesizing: "合成中",
  completed: "已完成",
};

function getStageDisplay(task: TaskStatus): string {
  if (task.status === "failed") return "任务失败";
  return STAGE_LABELS[task.stage];
}

function clampProgress(value: number): number {
  if (value < 0) return 0;
  if (value > 100) return 100;
  return Math.round(value);
}

function formatCurrentPage(task: TaskStatus): number {
  if (task.totalPages <= 0) return 0;
  if (task.status === "completed") return task.totalPages;
  return Math.min(task.currentPage + 1, task.totalPages);
}

export function ProgressBar({ task, connectionState, reconnectAttempt, message }: ProgressBarProps) {
  const progress = clampProgress(task.progress);
  const currentPage = formatCurrentPage(task);

  return (
    <section className="progress-bar" aria-live="polite">
      <h3>任务进度</h3>
      <p>
        当前页：{currentPage} / {task.totalPages || 0}
      </p>
      <p>阶段：{getStageDisplay(task)}</p>
      <p>百分比：{progress}%</p>
      {message ? <p>消息：{message}</p> : null}
      <div role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress} className="progress-bar__track">
        <div className="progress-bar__fill" style={{ width: `${progress}%` }} />
      </div>
      {connectionState !== "idle" &&
       connectionState !== "connected" &&
       task.status !== "completed" &&
       task.status !== "failed" ? (
        <p className="progress-bar__reconnect">
          {connectionState === "reconnecting"
            ? `连接断开，正在重连${reconnectAttempt > 0 ? `（第 ${reconnectAttempt} 次）` : ""}...`
            : connectionState === "error"
              ? "连接异常，请刷新重试"
              : "连接已断开"}
        </p>
      ) : null}
    </section>
  );
}
