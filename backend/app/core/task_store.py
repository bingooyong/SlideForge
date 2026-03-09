from __future__ import annotations

import threading
import time
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel


TaskStatusEnum = Literal["queued", "processing", "completed", "failed"]
TaskStageEnum = Literal["uploading", "processing", "synthesizing", "completed"]


class TaskStatus(BaseModel):
    taskId: str
    filename: Optional[str] = None
    status: TaskStatusEnum = "queued"
    progress: int = 0
    currentPage: int = 0
    totalPages: int = 1
    stage: TaskStageEnum = "uploading"
    failedPages: List[int] = []
    # 每个失败页的错误原因，key 为 0-based 页索引，value 为简要错误信息
    failureReasons: Optional[Dict[int, str]] = None
    # 真实导出 PPTX 文件的本地路径，供 /export/{taskId} 使用
    exportPath: Optional[str] = None


class InMemoryTaskStore:
    """
    进程内任务存储，供上传、任务查询与 WebSocket 共享使用。

    注意：这是开发阶段占位实现，不适合多进程/分布式环境。
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskStatus] = {}
        self._lock = threading.Lock()

    def create_task(self, task: TaskStatus) -> TaskStatus:
        with self._lock:
            self._tasks[task.taskId] = task
            return task

    def get_task(self, task_id: str) -> Optional[TaskStatus]:
        with self._lock:
            task = self._tasks.get(task_id)
            return task

    def update_task(self, task_id: str, **fields) -> Optional[TaskStatus]:
        with self._lock:
            existing = self._tasks.get(task_id)
            if existing is None:
                return None

            updated = existing.copy(update=fields)
            self._tasks[task_id] = updated
            return updated

    def mark_completed(self, task_id: str) -> Optional[TaskStatus]:
        return self.update_task(
            task_id,
            status="completed",
            stage="completed",
            progress=100,
        )


def run_mock_task(task_id: str, store: InMemoryTaskStore, total_pages: int = 5) -> None:
    """
    在后台线程中执行的占位任务逻辑：
    通过 sleep 模拟处理过程，并不断更新任务状态。
    """
    # 初始化为 processing 阶段
    store.update_task(
        task_id,
        status="processing",
        stage="processing",
        progress=0,
        currentPage=0,
        totalPages=total_pages,
    )

    for page_index in range(total_pages):
        progress = int((page_index + 1) / total_pages * 100)

        store.update_task(
            task_id,
            status="processing",
            stage="processing",
            progress=progress,
            currentPage=page_index,
            totalPages=total_pages,
        )

        time.sleep(0.5)

    store.mark_completed(task_id)

