from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.config import settings
from app.core.task_store import InMemoryTaskStore, TaskStatus
from app.dependencies import get_task_store


router = APIRouter(tags=["Export"])


def _task_output_pptx_path(task_id: str) -> Path:
    """任务目录下的 output.pptx 路径，与 pipeline 写入位置一致。重启后导出依赖此路径。"""
    return Path(settings.UPLOAD_DIR) / "tasks" / task_id / "output.pptx"


@router.get("/export/{taskId}")
async def export_pptx(
    taskId: str,
    task_store: InMemoryTaskStore = Depends(get_task_store),
):
    """
    导出指定任务生成的真实 PPTX 文件。

    - 若任务不存在且磁盘上无该任务的 output.pptx：返回 404
    - 若任务在内存中但尚未完成或尚未生成 PPTX：返回 202（TaskNotReady）
    - 若任务已完成且存在导出文件，或磁盘上存在该任务的 output.pptx（如重启后）：以二进制流形式返回
    """
    task: TaskStatus | None = task_store.get_task(taskId)
    pptx_path: Path | None = None
    download_stem: str = "presentation"

    if task is not None:
        if task.status != "completed" or not task.exportPath:
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Task not ready for export",
            )
        pptx_path = Path(task.exportPath)
        download_stem = Path(task.filename or "presentation").stem
    else:
        # 重启后内存任务丢失：若任务目录下仍有 output.pptx 则直接提供下载
        pptx_path = _task_output_pptx_path(taskId)
        if not pptx_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        download_stem = taskId

    if not pptx_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not found",
        )

    download_name = f"{download_stem}.pptx"
    file_handle = pptx_path.open("rb")

    return StreamingResponse(
        file_handle,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "presentationml.presentation"
        ),
        headers={
            "Content-Disposition": f'attachment; filename="{download_name}"'
        },
    )

