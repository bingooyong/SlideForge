import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.core.task_store import InMemoryTaskStore, TaskStatus
from app.dependencies import get_task_store


router = APIRouter()


def _task_to_progress_message(task: TaskStatus) -> dict:
    """
    将任务状态转换为 WebSocketProgress 契约格式的消息。
    包含 status 以便前端区分 completed 与 failed。
    """
    if task.stage != "completed":
        msg = f"Processing page {task.currentPage + 1} of {task.totalPages}"
    elif task.status == "failed":
        msg = "Task failed"
    else:
        msg = "Task completed"

    payload = {
        "taskId": task.taskId,
        "pageIndex": task.currentPage,
        "totalPages": task.totalPages,
        "stage": task.stage,
        "progress": task.progress,
        "status": task.status,
        "message": msg,
    }
    if task.failedPages:
        payload["failedPages"] = task.failedPages
    return payload


@router.websocket("/ws/progress")
async def websocket_progress(
    websocket: WebSocket,
    task_store: InMemoryTaskStore = Depends(get_task_store),
) -> None:
    """
    WebSocket 端点：按任务存储中的状态推送进度更新。

    Query parameter:
    - task_id: string task identifier (required)
    """
    task_id: Optional[str] = websocket.query_params.get("task_id")

    await websocket.accept()

    if not task_id:
        await websocket.send_json({"error": "task_id query parameter is required"})
        await websocket.close()
        return

    try:
        while True:
            task = task_store.get_task(task_id)
            if task is None:
                await websocket.send_json({"error": "Task not found"})
                break

            await websocket.send_json(_task_to_progress_message(task))

            if task.status in ("completed", "failed"):
                await websocket.close(code=1000)
                return

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        return

