"""默认图标资源：用于 icon_text_layout 在未显式传入 icon_images 时的兜底渲染。

LLM 生成的 JSON 中 icon 通过 icon_text_layout 的 placeholder_id（及可选的 icon/icon_properties.bbox）表示。
支持的语义与推荐/兼容的 placeholder_id：
  - 对号/通过：check, icon_check, checkmark, checkmark_circle, icon_checkmark_circle
  - 锁/安全：lock, icon_lock

渲染时从 elem 或 elem.icon_properties 取 placeholder_id，经 resolve_icon 或 build_default_icon_images 映射得到 PNG bytes 后插入幻灯片。
"""

from __future__ import annotations

import io
import logging
from functools import lru_cache
from typing import Dict, Optional

from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

# 规范语义 -> 所有已知别名（含 LLM 常见输出），单一数据源，新增变体只改此处
PLACEHOLDER_ALIASES: Dict[str, list[str]] = {
    "check": [
        "check",
        "icon_check",
        "checkmark",
        "checkmark_circle",
        "icon_checkmark_circle",
    ],
    "lock": [
        "lock",
        "icon_lock",
    ],
}


def _normalize_icon_key(key: str) -> str:
    """归一化 placeholder_id 便于匹配：去前缀 icon_/icon-/ico_，去尾部数字与下划线。"""
    k = (key or "").strip().lower()
    if not k:
        return ""
    for prefix in ("icon_", "icon-", "ico_"):
        if k.startswith(prefix):
            k = k[len(prefix) :]
    while k and (k[-1].isdigit() or k[-1] in {"_", "-"}):
        k = k[:-1]
    return k


@lru_cache(maxsize=1)
def build_default_icon_images() -> Dict[str, bytes]:
    """返回 placeholder_id -> PNG bytes 的默认图标映射（含全部别名，供渲染层 O(1) 查找）。"""
    check_bytes = _build_check_icon()
    lock_bytes = _build_lock_icon()
    canonical: Dict[str, bytes] = {"check": check_bytes, "lock": lock_bytes}
    out: Dict[str, bytes] = {}
    for canonical_key, aliases in PLACEHOLDER_ALIASES.items():
        if canonical_key not in canonical:
            continue
        for alias in aliases:
            out[alias] = canonical[canonical_key]
    return out


def resolve_icon(
    placeholder_id: str,
    icon_images: Optional[Dict[str, bytes]] = None,
) -> Optional[bytes]:
    """
    解析图标：先查传入字典，再查内置别名。如果都没命中，自动生成一个万能圆点图标兜底！
    """
    if not placeholder_id or not placeholder_id.strip():
        return None
    source = icon_images if icon_images is not None else build_default_icon_images()
    if placeholder_id in source:
        return source[placeholder_id]
    wanted = _normalize_icon_key(placeholder_id)
    for k, v in source.items():
        if _normalize_icon_key(k) == wanted:
            return v
    logger.info("Icon unresolved, using generic fallback: placeholder_id=%r", placeholder_id)
    return _build_generic_bullet_icon()


def _build_generic_bullet_icon(size: int = 72) -> bytes:
    """万能通用圆点图标：未命中时占位，用户可在 PPT 中右键「更改图片」替换。"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = int(size * 0.25)
    draw.ellipse((pad, pad, size - pad, size - pad), fill=(62, 111, 199, 255))
    return _to_png_bytes(img)


def _build_check_icon(size: int = 72) -> bytes:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = int(size * 0.08)
    draw.ellipse((pad, pad, size - pad, size - pad), fill=(74, 119, 168, 255))

    points = [
        (int(size * 0.30), int(size * 0.52)),
        (int(size * 0.45), int(size * 0.67)),
        (int(size * 0.72), int(size * 0.36)),
    ]
    draw.line(points, fill=(255, 255, 255, 255), width=max(3, int(size * 0.10)), joint="curve")

    return _to_png_bytes(img)


def _build_lock_icon(size: int = 72) -> bytes:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    body_x0 = int(size * 0.22)
    body_y0 = int(size * 0.40)
    body_x1 = int(size * 0.78)
    body_y1 = int(size * 0.84)
    draw.rounded_rectangle(
        (body_x0, body_y0, body_x1, body_y1),
        radius=int(size * 0.08),
        fill=(62, 111, 199, 255),
    )

    shackle_x0 = int(size * 0.32)
    shackle_y0 = int(size * 0.16)
    shackle_x1 = int(size * 0.68)
    shackle_y1 = int(size * 0.50)
    draw.arc(
        (shackle_x0, shackle_y0, shackle_x1, shackle_y1),
        start=190,
        end=-10,
        fill=(62, 111, 199, 255),
        width=max(3, int(size * 0.08)),
    )

    keyhole_r = int(size * 0.05)
    cx = size // 2
    cy = int(size * 0.58)
    draw.ellipse((cx - keyhole_r, cy - keyhole_r, cx + keyhole_r, cy + keyhole_r), fill=(255, 255, 255, 255))
    draw.rectangle(
        (cx - max(1, keyhole_r // 3), cy, cx + max(1, keyhole_r // 3), cy + int(size * 0.11)),
        fill=(255, 255, 255, 255),
    )

    return _to_png_bytes(img)


def _to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
