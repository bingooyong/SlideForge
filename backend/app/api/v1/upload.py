from typing import Optional
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status

from app.config import settings
from app.core.logging import get_logger
from app.core.task_store import InMemoryTaskStore, TaskStatus
from app.dependencies import get_task_store
from app.pipeline.pdf_to_images import (
    EmptyPDFError,
    EncryptedPDFError,
    PDFConversionError,
    get_pdf_page_count,
)
from app.pipeline.pipeline_service import PipelineResult, PipelineService, ProgressEvent
from app.pipeline.recompose_from_task_dir import recompose_pptx_from_task_dir

from .task_io import get_task_dir, get_task_input_path


router = APIRouter(tags=["Upload"])


def _task_data_root() -> Path:
    """
    返回任务数据根目录。

    目前实现为 {settings.UPLOAD_DIR}/tasks，后续可在配置中独立抽出。
    """
    return Path(settings.UPLOAD_DIR) / "tasks"


# 允许的图片扩展名（直接保存为 input.*，流水线按单页处理）
_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".bmp"})


def _run_pipeline_task(
    task_id: str,
    pdf_path: str,
    mode: str,
    aspect_ratio: str,
    task_store: InMemoryTaskStore,
    api_key: Optional[str] = None,
) -> None:
    """
    在后台线程中运行真实 PDF → PPTX 流水线，并持续更新任务状态。
    """

    def on_progress(event: ProgressEvent) -> None:
        stage = "processing"
        if event.stage == "pptx":
            stage = "synthesizing"

        task_store.update_task(
            event.task_id,
            status="processing",
            stage=stage,
            progress=event.progress,
            currentPage=event.page_index,
            totalPages=event.total_pages,
        )

    service = PipelineService(default_output_root=_task_data_root())

    try:
        result: PipelineResult = service.run(
            task_id=task_id,
            pdf_path=pdf_path,
            mode=mode,
            aspect_ratio=aspect_ratio,
            progress_callback=on_progress,
            api_key=api_key,
        )
    except Exception as exc:
        logger = get_logger("upload.pipeline_task")
        logger.error(
            "pipeline_task_fatal",
            task_id=task_id,
            stage="pipeline_run",
            pdf_path=pdf_path,
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True,
        )
        task_store.update_task(
            task_id,
            status="failed",
            stage="completed",
            progress=100,
        )
        return

    # 汇总失败页原因，供后续 Task 4.2 使用
    failure_reasons = {
        r.page_index: r.error for r in result.page_results if not r.success and r.error
    } or None

    if result.output_pptx_path is not None and any(r.success for r in result.page_results):
        task_store.update_task(
            task_id,
            status="completed",
            stage="completed",
            progress=100,
            totalPages=result.total_pages,
            failedPages=result.failed_pages,
            failureReasons=failure_reasons,
            exportPath=str(result.output_pptx_path),
        )
    else:
        task_store.update_task(
            task_id,
            status="failed",
            stage="completed",
            progress=100,
            totalPages=result.total_pages,
            failedPages=result.failed_pages,
            failureReasons=failure_reasons,
        )


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("standard"),
    aspectRatio: str = Form("16:9"),
    apiKey: Optional[str] = Form(None),
    task_store: InMemoryTaskStore = Depends(get_task_store),
):
    """
    真实上传端点：
    - 支持 PDF 或图片（jpg/png/webp/bmp）；PDF 保存为 input.pdf，图片保存为 input.<ext>，流水线统一按「页」处理（图片即单页）
    - 在 InMemoryTaskStore 中创建任务记录
    - 使用 BackgroundTasks 启动真实 pipeline 后台任务
    - 返回与 OpenAPI UploadResponse 对齐的元信息（包括 pageCount）
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    fn_lower = file.filename.lower()
    ext = Path(file.filename).suffix.lower()
    is_pdf = ext == ".pdf"
    is_image = ext in _IMAGE_EXTENSIONS
    if not is_pdf and not is_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"仅支持 PDF 或图片（{', '.join(_IMAGE_EXTENSIONS)}）上传。",
        )

    task_id = str(uuid.uuid4())
    root = _task_data_root()
    task_dir = root / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    content = await file.read()

    if is_pdf:
        input_path = task_dir / "input.pdf"
        if len(content) < 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF 文件过小，请上传有效的 PDF（至少约 1KB）。",
            )
        input_path.write_bytes(content)
        try:
            page_count = get_pdf_page_count(str(input_path))
        except EncryptedPDFError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except EmptyPDFError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except PDFConversionError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            ) from exc
    else:
        # 图片：直接保存为 input.<ext>，流水线按单页处理，不转 PDF
        if len(content) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片文件为空。",
            )
        input_path = task_dir / f"input{ext}"
        input_path.write_bytes(content)
        page_count = 1

    task = TaskStatus(
        taskId=task_id,
        filename=file.filename,
        status="queued",
        progress=0,
        currentPage=0,
        totalPages=page_count,
        stage="uploading",
        failedPages=[],
    )
    task_store.create_task(task)

    background_tasks.add_task(
        _run_pipeline_task,
        task_id,
        str(input_path),
        mode,
        aspectRatio,
        task_store,
        apiKey,
    )

    return {
        "taskId": task.taskId,
        "filename": task.filename,
        "pageCount": task.totalPages,
        "status": task.status,
    }


@router.post("/recompose/{taskId}", status_code=status.HTTP_200_OK)
async def recompose_pptx(
    taskId: str,
    aspectRatio: str = Form("16:9"),
    task_store: InMemoryTaskStore = Depends(get_task_store),
):
    """
    仅从任务目录已有 page_*_llm_raw_v2.txt 与 page_*_input.png 重新合成 output.pptx，不调用大模型。
    与 scripts/run_pptx_from_raw.py 逻辑一致，适合重启后或改完合成代码后快速重出 PPTX。
    """
    root = _task_data_root()
    task_dir = root / taskId
    if not task_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task directory not found",
        )
    try:
        out_path, total_pages = recompose_pptx_from_task_dir(task_dir, aspect_ratio=aspectRatio)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (ValueError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    task = TaskStatus(
        taskId=taskId,
        filename=None,
        status="completed",
        progress=100,
        currentPage=total_pages - 1,
        totalPages=total_pages,
        stage="completed",
        failedPages=[],
        exportPath=str(out_path),
    )
    task_store.create_task(task)

    return {
        "taskId": taskId,
        "status": "completed",
        "exportPath": str(out_path),
        "message": "PPTX recomposed from cached raw; use GET /api/v1/export/{taskId} to download.",
    }


@router.post("/regenerate/{taskId}", status_code=status.HTTP_202_ACCEPTED)
async def regenerate_pptx(
    taskId: str,
    background_tasks: BackgroundTasks,
    mode: str = Form("standard"),
    aspectRatio: str = Form("16:9"),
    task_store: InMemoryTaskStore = Depends(get_task_store),
):
    """
    对已有任务重新跑流水线生成 PPTX（适用于重启后任务不在内存、但任务目录和输入文件仍在的场景）。
    - 若任务目录或 input.pdf / input.<图片扩展> 不存在：返回 404
    - 否则在后台重新执行流水线，覆盖 output.pptx，并更新任务状态
    - 客户端可轮询 GET /tasks/{taskId} 查状态，完成后通过 GET /export/{taskId} 下载
    """
    task_dir = get_task_dir(taskId)
    if not task_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    input_path = get_task_input_path(taskId)
    if input_path is None or not input_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task input file missing (cannot regenerate)",
        )

    if input_path.suffix.lower() == ".pdf":
        try:
            page_count = get_pdf_page_count(str(input_path))
        except (EncryptedPDFError, EmptyPDFError, PDFConversionError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
    else:
        page_count = 1

    task = TaskStatus(
        taskId=taskId,
        filename=None,
        status="queued",
        progress=0,
        currentPage=0,
        totalPages=page_count,
        stage="uploading",
        failedPages=[],
    )
    task_store.create_task(task)

    background_tasks.add_task(
        _run_pipeline_task,
        taskId,
        str(input_path),
        mode,
        aspectRatio,
        task_store,
    )

    return {
        "taskId": taskId,
        "status": "queued",
        "message": "Regeneration started; poll GET /api/v1/tasks/{taskId} for progress, then GET /api/v1/export/{taskId} when completed.",
    }

