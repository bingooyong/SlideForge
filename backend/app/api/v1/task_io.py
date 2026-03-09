"""任务目录与输入文件路径解析，供 upload / tasks / export 等复用。"""
from pathlib import Path
from typing import Optional

from app.config import settings

_TASK_ROOT = Path(settings.UPLOAD_DIR) / "tasks"
_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


def get_task_dir(task_id: str) -> Path:
    return _TASK_ROOT / task_id


def get_task_input_path(task_id: str) -> Optional[Path]:
    """
    返回该任务的输入文件路径：input.pdf 或 input.<图片扩展名>。
    若都不存在则返回 None。
    """
    task_dir = get_task_dir(task_id)
    if not task_dir.is_dir():
        return None
    p = task_dir / "input.pdf"
    if p.is_file():
        return p
    for ext in _IMAGE_EXTS:
        p = task_dir / f"input{ext}"
        if p.is_file():
            return p
    return None
