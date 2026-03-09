from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import io

from PIL import Image

from app.pipeline.pdf_to_images import PageImage
from app.pipeline.layout_ocr_models import ImageBlock


class IconCroppingError(Exception):
    """图标/非文本区域裁剪过程中的通用错误。"""


@dataclass
class CroppedImage:
    """裁剪后的图像结果。"""

    block_id: str
    page_number: int
    image_bytes: bytes
    width: int
    height: int


def _clamp_bbox(x: int, y: int, w: int, h: int, img_w: int, img_h: int) -> Optional[tuple[int, int, int, int]]:
    if w <= 0 or h <= 0:
        return None

    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(img_w, x + w)
    y1 = min(img_h, y + h)

    if x1 <= x0 or y1 <= y0:
        return None

    return x0, y0, x1, y1


def crop_imageblocks(
    page_image: PageImage,
    image_blocks: List[ImageBlock],
    icon_expand_ratio: float = 0.05,
    make_white_transparent: bool = False,
) -> List[Optional[CroppedImage]]:
    """
    根据 ImageBlock 的归一化 bbox，从原始页面图中裁剪非文本区域。

    - 对于 bbox 越界、面积过小等情况，返回 None 而不是抛出异常。
    - 若 make_white_transparent=True，则尝试将接近白色的背景设为透明。

    返回列表长度与 image_blocks 相同，按顺序一一对应。
    """
    try:
        with Image.open(io.BytesIO(page_image.image_bytes)) as base_img:
            base_img = base_img.convert("RGBA")
            img_w, img_h = base_img.size

            results: List[Optional[CroppedImage]] = []

            for block in image_blocks:
                box = block.box
                # Slide Schema 中 box 使用 0-1 归一化坐标，这里换算为像素
                x = int(box.x * img_w)
                y = int(box.y * img_h)
                w = int(box.w * img_w)
                h = int(box.h * img_h)

                # 可选：对可能是“图标”的块适度扩展边界
                # 目前 Schema 中没有显式 icon 类型，这里仅保留接口，未来可按 metadata 或自定义字段启用
                if icon_expand_ratio > 0:
                    expand_x = int(w * icon_expand_ratio)
                    expand_y = int(h * icon_expand_ratio)
                    x -= expand_x
                    y -= expand_y
                    w += 2 * expand_x
                    h += 2 * expand_y

                clamped = _clamp_bbox(x, y, w, h, img_w, img_h)
                if clamped is None:
                    results.append(None)
                    continue

                x0, y0, x1, y1 = clamped
                cropped = base_img.crop((x0, y0, x1, y1))

                if make_white_transparent:
                    # 简单白底转透明：对接近白色的像素设置 alpha=0
                    datas = list(cropped.getdata())
                    new_data = []
                    for r, g, b, a in datas:
                        if r > 245 and g > 245 and b > 245:
                            new_data.append((r, g, b, 0))
                        else:
                            new_data.append((r, g, b, a))
                    cropped.putdata(new_data)

                buffer = io.BytesIO()
                cropped.save(buffer, format="PNG")
                results.append(
                    CroppedImage(
                        block_id=block.id,
                        page_number=page_image.page_number,
                        image_bytes=buffer.getvalue(),
                        width=cropped.width,
                        height=cropped.height,
                    )
                )

            return results
    except Exception as exc:
        # 整体失败时抛出一次性错误，由上游决定如何降级
        raise IconCroppingError(f"Failed to crop image blocks: {exc}") from exc

