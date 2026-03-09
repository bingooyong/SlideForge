import { useEffect, useRef, useState } from "react";

export type WebSocketConnectionState =
  | "idle"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "disconnected"
  | "error";

export interface WebSocketProgressMessage {
  taskId: string;
  pageIndex: number;
  totalPages: number;
  stage: "uploading" | "processing" | "synthesizing" | "completed";
  progress: number;
  status?: "queued" | "processing" | "completed" | "failed";
  message?: string;
  failedPages?: number[];
}

interface UseWebSocketOptions {
  taskId: string | null;
  enabled?: boolean;
  onProgressMessage?: (message: WebSocketProgressMessage) => void;
}

interface UseWebSocketResult {
  connectionState: WebSocketConnectionState;
  lastMessage: WebSocketProgressMessage | null;
  lastError: string | null;
  reconnectAttempt: number;
}

const MAX_RECONNECT_DELAY_MS = 8_000;

function buildWebSocketUrl(taskId: string): string {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/api/v1/ws/progress?task_id=${encodeURIComponent(taskId)}`;
}

function isProgressMessage(payload: unknown): payload is WebSocketProgressMessage {
  if (!payload || typeof payload !== "object") return false;
  const candidate = payload as Record<string, unknown>;
  return (
    typeof candidate.taskId === "string" &&
    typeof candidate.pageIndex === "number" &&
    typeof candidate.totalPages === "number" &&
    typeof candidate.stage === "string" &&
    typeof candidate.progress === "number"
  );
}

export function useWebSocket({
  taskId,
  enabled = true,
  onProgressMessage,
}: UseWebSocketOptions): UseWebSocketResult {
  const [connectionState, setConnectionState] = useState<WebSocketConnectionState>("idle");
  const [lastMessage, setLastMessage] = useState<WebSocketProgressMessage | null>(null);
  const [lastError, setLastError] = useState<string | null>(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);

  const websocketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const shouldReconnectRef = useRef(false);
  const reconnectAttemptRef = useRef(0);

  useEffect(() => {
    if (!taskId || !enabled) {
      setConnectionState("idle");
      return;
    }

    shouldReconnectRef.current = true;

    const clearReconnectTimer = () => {
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    const connect = () => {
      clearReconnectTimer();
      setConnectionState(reconnectAttemptRef.current > 0 ? "reconnecting" : "connecting");

      const websocket = new WebSocket(buildWebSocketUrl(taskId));
      websocketRef.current = websocket;

      websocket.onopen = () => {
        reconnectAttemptRef.current = 0;
        setReconnectAttempt(0);
        setLastError(null);
        setConnectionState("connected");
      };

      websocket.onmessage = (event) => {
        try {
          const payload: unknown = JSON.parse(event.data);
          if (!isProgressMessage(payload)) {
            if (payload && typeof payload === "object" && "error" in payload) {
              setLastError(String((payload as { error: unknown }).error ?? "WebSocket 返回错误消息"));
            }
            return;
          }
          // 任务已结束：禁止在 onclose 时重连，避免 ECONNRESET 后反复重连
          if (payload.status === "completed" || payload.status === "failed") {
            shouldReconnectRef.current = false;
          }
          setLastMessage(payload);
          onProgressMessage?.(payload);
        } catch {
          setLastError("WebSocket 消息解析失败");
        }
      };

      websocket.onerror = () => {
        setConnectionState("error");
        setLastError("WebSocket 连接发生错误");
      };

      websocket.onclose = () => {
        websocketRef.current = null;
        if (!shouldReconnectRef.current) {
          setConnectionState("disconnected");
          return;
        }

        reconnectAttemptRef.current += 1;
        setReconnectAttempt(reconnectAttemptRef.current);
        setConnectionState("reconnecting");

        const delay = Math.min(1000 * 2 ** (reconnectAttemptRef.current - 1), MAX_RECONNECT_DELAY_MS);
        reconnectTimerRef.current = window.setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      shouldReconnectRef.current = false;
      clearReconnectTimer();
      if (websocketRef.current) {
        websocketRef.current.close();
        websocketRef.current = null;
      }
      setConnectionState("disconnected");
    };
  }, [enabled, onProgressMessage, taskId]);

  return {
    connectionState,
    lastMessage,
    lastError,
    reconnectAttempt,
  };
}

