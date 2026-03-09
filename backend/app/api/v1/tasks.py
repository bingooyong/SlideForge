from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.core.task_store import InMemoryTaskStore, TaskStatus
from app.dependencies import get_task_store
from app.pipeline.pdf_to_images import (
    PDFConversionError,
    get_page_thumbnail,
)

from .task_io import get_task_input_path


router = APIRouter(tags=["Tasks"])

# 图片扩展名 -> 预览返回的 media_type
_PREVIEW_MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


@router.get("/tasks/{taskId}", response_model=TaskStatus)
async def get_task_status(
    taskId: str,
    task_store: InMemoryTaskStore = Depends(get_task_store),
) -> TaskStatus:
    """
    根据任务存储返回指定 taskId 的实时状态。
    """
    task = task_store.get_task(taskId)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.get("/tasks/{taskId}/preview/{pageIndex}", response_class=Response)
async def get_task_page_preview(
    taskId: str,
    pageIndex: int,
) -> Response:
    """
    返回指定任务、指定页的缩略图。PDF 为渲染缩略图；图片任务仅一页，返回原图。
    """
    if pageIndex < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="pageIndex must be >= 0")
    input_path = get_task_input_path(taskId)
    if input_path is None or not input_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task input not found")
    ext = input_path.suffix.lower()
    if ext in _PREVIEW_MEDIA_TYPES:
        if pageIndex != 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image task has only one page (index 0)")
        return Response(
            content=input_path.read_bytes(),
            media_type=_PREVIEW_MEDIA_TYPES[ext],
        )
    try:
        thumb_bytes = get_page_thumbnail(str(input_path), pageIndex)
    except (ValueError, PDFConversionError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return Response(content=thumb_bytes, media_type="image/png")

