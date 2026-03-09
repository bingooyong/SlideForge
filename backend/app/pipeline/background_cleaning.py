from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import io

import cv2
import numpy as np
from PIL import Image

from app.pipeline.pdf_to_images import PageImage
from app.pipeline.layout_ocr_models import TextBlock


class BackgroundCleaningError(Exception):
    """背景净化（去字/修复）过程中的通用错误。"""


@dataclass
class CleanedBackground:
    """去字或降级后的背景结果。"""
    page_number: int
    image_bytes: bytes
    width: int
    height: int
    method: str  # "solid_fallback", "inpaint_telea", "none", "failed_fallback"


def _build_mask(
    page_image: PageImage,
    text_blocks: List[TextBlock],
    expand_ratio: float = 0.02,
) -> Optional[np.ndarray]:
    """
    根据 TextBlock 的归一化 bbox 生成二值 mask。
    """
    if not text_blocks:
        return None

    img_w, img_h = page_image.width, page_image.height
    mask = np.zeros((img_h, img_w), dtype=np.uint8)

    has_foreground = False
    for tb in text_blocks:
        box = tb.box
        x = int(box.x * img_w)
        y = int(box.y * img_h)
        w = int(box.w * img_w)
        h = int(box.h * img_h)

        if w <= 0 or h <= 0:
            continue

        expand_x = int(w * expand_ratio)
        expand_y = int(h * expand_ratio)
        x0 = max(0, x - expand_x)
        y0 = max(0, y - expand_y)
        x1 = min(img_w, x + w + expand_x)
        y1 = min(img_h, y + h + expand_y)

        if x1 <= x0 or y1 <= y0:
            continue

        mask[y0:y1, x0:x1] = 255
        has_foreground = True

    return mask if has_foreground else None


def _add_corner_watermark_mask(
    mask: np.ndarray,
    img_h: int,
    img_w: int,
    corner_ratio_w: float = 0.12,
    corner_ratio_h: float = 0.08,
) -> None:
    """消除右下角的 NotebookLM 水印。"""
    cw = max(2, int(img_w * corner_ratio_w))
    ch = max(2, int(img_h * corner_ratio_h))
    x0, y0 = img_w - cw, img_h - ch
    mask[y0:img_h, x0:img_w] = 255


def clean_background(
    page_image: PageImage,
    text_blocks: List[TextBlock],
    expand_ratio: float = 0.02,
) -> CleanedBackground:
    """
    背景净化（智能纯色回退版）：
    遮罩占比 > 15% 时直接铺主色调纯色（从未遮挡区域取中位数色，失败则白底）；
    小面积时用 INPAINT_TELEA 擦除，坚决不用 INPAINT_NS 避免条纹崩溃。
    """
    try:
        with Image.open(io.BytesIO(page_image.image_bytes)) as img:
            img = img.convert("RGB")
            rgb = np.array(img)
    except Exception as exc:
        raise BackgroundCleaningError(f"Failed to decode image bytes: {exc}") from exc

    if rgb.size == 0:
        raise BackgroundCleaningError("Image array is empty.")

    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    img_h, img_w = bgr.shape[:2]

    mask = _build_mask(page_image, text_blocks, expand_ratio=expand_ratio)
    if mask is None:
        mask = np.zeros((img_h, img_w), dtype=np.uint8)

    _add_corner_watermark_mask(mask, img_h, img_w)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel)

    if not np.any(mask):
        return CleanedBackground(
            page_image.page_number,
            page_image.image_bytes,
            img_w,
            img_h,
            "none",
        )

    mask_ratio = float(np.count_nonzero(mask)) / (img_h * img_w)

    result_bgr: np.ndarray
    method = "unknown"

    if mask_ratio > 0.15:
        unmasked_pixels = bgr[mask == 0]

        if len(unmasked_pixels) > (img_w * img_h * 0.02):
            bg_color = np.median(unmasked_pixels, axis=0).astype(np.uint8)
        else:
            bg_color = np.array([255, 255, 255], dtype=np.uint8)

        result_bgr = np.full((img_h, img_w, 3), bg_color, dtype=np.uint8)
        method = "solid_fallback"

    else:
        try:
            result_bgr = cv2.inpaint(
                bgr, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA
            )
            method = "inpaint_telea"
        except Exception:
            result_bgr = np.full((img_h, img_w, 3), 255, dtype=np.uint8)
            method = "failed_fallback"

    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
    out_img = Image.fromarray(result_rgb)
    buffer = io.BytesIO()
    out_img.save(buffer, format="PNG")

    return CleanedBackground(
        page_number=page_image.page_number,
        image_bytes=buffer.getvalue(),
        width=out_img.width,
        height=out_img.height,
        method=method,
    )
