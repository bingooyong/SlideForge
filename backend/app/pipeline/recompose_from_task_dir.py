"""
从任务目录已有的 page_*_llm_raw_v2.txt 与 page_*_input.png 重新合成 output.pptx，不调用大模型。

与 scripts/run_pptx_from_raw.py 单页逻辑一致，按页循环后写入 task_dir/output.pptx。
"""
from __future__ import annotations

import io
import re
from pathlib import Path
from typing import List

from pptx import Presentation
from pydantic import ValidationError
from PIL import Image

from app.pipeline.layout_ocr_models import parse_slide_json, strip_markdown_json
from app.pipeline.layout_ocr import _normalize_page_elements_to_elements
from app.pipeline.slide_schema_v2 import SlideDocumentV2, slide_document_v2_to_text_blocks_for_mask
from app.pipeline.pptx_composition import setup_slide_size
from app.pipeline.pptx_composition_v2 import create_slide_v2
from app.pipeline.background_cleaning import clean_background
from app.pipeline.pdf_to_images import PageImage


_MASK_TYPES = {"text_box", "text_block", "shape_text_box", "icon_text_layout", "list_block", "list_layout", "group"}


def _collect_bboxes_from_dict(doc: dict) -> List[List[float]]:
    """从 dict 的 elements 收集绝对 bbox [x,y,w,h]（0~1），用于蒙版。"""
    elements = doc.get("slide_data", {}).get("elements", doc.get("elements", []))
    if not elements:
        return []

    out: List[List[float]] = []

    def walk(elem: dict, px: float, py: float, pw: float, ph: float) -> None:
        bbox = elem.get("bbox")
        if not isinstance(bbox, list) or len(bbox) != 4:
            return
        try:
            cx, cy, cw, ch = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
        except (TypeError, ValueError):
            return
        abs_x = px + cx * pw
        abs_y = py + cy * ph
        abs_w = cw * pw
        abs_h = ch * ph
        abs_bbox = [abs_x, abs_y, abs_w, abs_h]
        elem_type = elem.get("type") or ""
        if elem_type in _MASK_TYPES:
            out.append(abs_bbox)
        if elem_type == "group":
            for child in elem.get("children") or []:
                if isinstance(child, dict):
                    walk(child, abs_x, abs_y, abs_w, abs_h)

    for elem in elements:
        if isinstance(elem, dict):
            walk(elem, 0.0, 0.0, 1.0, 1.0)
    return out


def _text_blocks_from_bboxes(bboxes: List[List[float]]):
    """将绝对 bbox 转为 clean_background 所需的 TextBlock 列表。"""
    from app.pipeline.layout_ocr_models import Box2D, TextBlock

    result = []
    for i, b in enumerate(bboxes):
        if len(b) != 4 or b[2] <= 0 or b[3] <= 0:
            continue
        result.append(
            TextBlock(
                id=f"recompose-mask-{i}",
                type="text",
                content="",
                box=Box2D(x=b[0], y=b[1], w=b[2], h=b[3]),
            )
        )
    return result


def _parse_raw_and_mask(raw_text: str) -> tuple[dict, list]:
    """解析 raw 文本，返回 (use_doc dict, text_blocks for mask)。与 run_pptx_from_raw 一致。"""
    raw_text = strip_markdown_json(raw_text)
    raw_json = parse_slide_json(raw_text)
    if not isinstance(raw_json, dict):
        raise ValueError("Parsed result is not a dict")
    _normalize_page_elements_to_elements(raw_json)

    try:
        doc_for_mask = SlideDocumentV2.model_validate(raw_json)
        text_blocks = slide_document_v2_to_text_blocks_for_mask(doc_for_mask)
    except ValidationError:
        bboxes = _collect_bboxes_from_dict(raw_json)
        text_blocks = _text_blocks_from_bboxes(bboxes)
    return raw_json, text_blocks


def _page_indices_from_task_dir(task_dir: Path) -> List[int]:
    """从 task_dir 中 page_*_llm_raw_v2.txt 解析出有序页码。"""
    indices: List[int] = []
    pattern = re.compile(r"^page_(\d+)_llm_raw_v2\.txt$")
    for p in task_dir.iterdir():
        if p.is_file():
            m = pattern.match(p.name)
            if m:
                indices.append(int(m.group(1)))
    return sorted(indices)


def recompose_pptx_from_task_dir(
    task_dir: Path,
    aspect_ratio: str = "16:9",
) -> tuple[Path, int]:
    """
    从任务目录已有 page_*_llm_raw_v2.txt 与 page_*_input.png 重新合成 output.pptx，不调 API。

    Returns:
        (生成的 output.pptx 路径, 页数)
    """
    task_dir = task_dir.resolve()
    indices = _page_indices_from_task_dir(task_dir)
    if not indices:
        raise FileNotFoundError(
            f"No page_*_llm_raw_v2.txt found in {task_dir}"
        )

    prs = Presentation()
    setup_slide_size(prs, aspect_ratio)

    for page_idx in indices:
        raw_path = task_dir / f"page_{page_idx}_llm_raw_v2.txt"
        image_path = task_dir / f"page_{page_idx}_input.png"
        if not raw_path.is_file():
            raise FileNotFoundError(f"Missing {raw_path.name}")
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing {image_path.name}")

        raw_text = raw_path.read_text(encoding="utf-8")
        use_doc, text_blocks = _parse_raw_and_mask(raw_text)

        with Image.open(image_path) as img:
            img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            page_image = PageImage(
                image_bytes=buf.getvalue(),
                width=img.width,
                height=img.height,
                page_number=page_idx + 1,
            )
        cleaned = clean_background(page_image, text_blocks=text_blocks)
        create_slide_v2(prs, use_doc, cleaned, icon_images=None)

    out_path = task_dir / "output.pptx"
    prs.save(str(out_path))
    return out_path, len(indices)
