#!/usr/bin/env python3
"""
从「版面 OCR 大模型原始输出」文件生成 PPTX，用于离线测试生成质量。

用法（在 backend 目录下）:
  # 指定 raw 文件与对应原图，生成 PPTX
  python scripts/run_pptx_from_raw.py assets/demo-001_llm_raw_gemini_gemini-2_5-flash_v2.txt --image ../assets/demo-001.jpg -o out.pptx

  # 不传 --image 时，会尝试根据 raw 文件名推断原图（如 demo-001_llm_raw_xxx.txt -> demo-001.jpg）
  python scripts/run_pptx_from_raw.py assets/demo-001_llm_raw_gemini_gemini-2_5-flash_v2.txt -o out.pptx

  # 不传 -o 时，输出为 <raw 文件名去掉 _llm_raw_xxx>.pptx
  python scripts/run_pptx_from_raw.py assets/demo-001_llm_raw_gemini_gemini-2_5-flash_v2.txt --image ../assets/demo-001.jpg

依赖：与 test_layout_ocr.py 相同（PIL、app.pipeline）。不调用大模型 API。
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptx import Presentation

from app.pipeline.layout_ocr_models import parse_slide_json, strip_markdown_json
from app.pipeline.slide_schema_v2 import SlideDocumentV2
from app.pipeline.pptx_composition import setup_slide_size
from app.pipeline.pptx_composition_v2 import create_slide_v2
from app.pipeline.background_cleaning import clean_background
from app.pipeline.pdf_to_images import PageImage
from app.pipeline.glm_v2_normalizer import normalize_glm_v2_output
from pydantic import ValidationError


# 需要参与背景蒙版的元素类型（与 slide_schema_v2.collect_text_bboxes_absolute 一致）
_MASK_TYPES = {"text_box", "text_block", "shape_text_box", "icon_text_layout", "list_block", "list_layout", "group"}


def _collect_bboxes_from_dict(doc: dict) -> list[list[float]]:
    """
    从 dict 结构的 V2 文档（含 slide_data.elements 或 elements）收集绝对 bbox [x,y,w,h]（0~1）。
    用于在无 SlideDocumentV2 时生成背景净化用的蒙版。
    """
    elements = doc.get("slide_data", {}).get("elements", doc.get("elements", []))
    if not elements:
        return []

    out: list[list[float]] = []

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


def _text_blocks_from_bboxes(bboxes: list[list[float]]):
    """将绝对 bbox 列表转为 clean_background 所需的 TextBlock 列表。"""
    from app.pipeline.layout_ocr_models import Box2D, TextBlock

    result = []
    for i, b in enumerate(bboxes):
        if len(b) != 4 or b[2] <= 0 or b[3] <= 0:
            continue
        result.append(
            TextBlock(
                id=f"raw-mask-{i}",
                type="text",
                content="",
                box=Box2D(x=b[0], y=b[1], w=b[2], h=b[3]),
            )
        )
    return result


def _infer_image_path(raw_path: Path) -> Path:
    """从 raw 文件名推断原图路径，如 demo-001_llm_raw_gemini_v2.txt -> demo-001.jpg。"""
    stem = raw_path.stem
    # 去掉 _llm_raw_* 或 _llm_raw_*_v2
    base = re.sub(r"_llm_raw_.*$", "", stem)
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        candidate = raw_path.parent / f"{base}{ext}"
        if candidate.is_file():
            return candidate
        # 也尝试上一级（如 assets 在 repo 根）
        candidate = raw_path.parent.parent / f"{base}{ext}"
        if candidate.is_file():
            return candidate
    return raw_path.parent / f"{base}.jpg"


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="从版面 OCR 原始输出文件生成 PPTX（不调 API）"
    )
    parser.add_argument(
        "raw_path",
        type=Path,
        help="大模型原始输出文件路径，如 assets/demo-001_llm_raw_gemini_gemini-2_5-flash_v2.txt",
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=None,
        help="对应原图路径，用于背景净化。不传则根据 raw 文件名推断（如 demo-001.jpg）",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="输出 PPTX 路径。不传则用 <原图名>.pptx",
    )
    args = parser.parse_args()

    raw_path = args.raw_path
    if not raw_path.is_file():
        print(f"错误: 文件不存在 {raw_path}", file=sys.stderr)
        sys.exit(1)

    # 1) 解析 raw
    raw_text = raw_path.read_text(encoding="utf-8")
    raw_text = strip_markdown_json(raw_text)
    try:
        raw_json = parse_slide_json(raw_text)
    except Exception as e:
        print(f"错误: 无法解析 JSON - {e}", file=sys.stderr)
        sys.exit(2)

    # 蒙版用 model 或 dict 收集 bbox；渲染必须用原始 dict，否则 Pydantic 会丢弃 content/runs 等未定义字段导致无文字。
    if isinstance(raw_json, dict):
        try:
            doc_for_mask = SlideDocumentV2.model_validate(raw_json)
            from app.pipeline.slide_schema_v2 import slide_document_v2_to_text_blocks_for_mask
            text_blocks = slide_document_v2_to_text_blocks_for_mask(doc_for_mask)
        except ValidationError:
            normalize_glm_v2_output(raw_json)
            bboxes = _collect_bboxes_from_dict(raw_json)
            text_blocks = _text_blocks_from_bboxes(bboxes)
        use_doc = raw_json  # 始终把 dict 传给 create_slide_v2，保留 content.runs 等
    else:
        use_doc = raw_json
        text_blocks = []
    print(f"[1] 蒙版 TextBlock 数量: {len(text_blocks)}")

    # 3) 背景图
    image_path = args.image or _infer_image_path(raw_path)
    if not image_path.is_file():
        print(f"错误: 未找到原图 {image_path}，请用 --image 指定", file=sys.stderr)
        sys.exit(3)

    from PIL import Image
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        page_image = PageImage(
            image_bytes=buf.getvalue(),
            width=img.width,
            height=img.height,
            page_number=1,
        )
    cleaned = clean_background(page_image, text_blocks=text_blocks)
    print(f"[2] 背景: {image_path} 经 clean_background 净化")

    # 4) 生成 PPTX
    prs = Presentation()
    setup_slide_size(prs, "16:9")
    create_slide_v2(prs, use_doc, cleaned, icon_images=None)
    out_path = args.output
    if out_path is None:
        base = _infer_image_path(raw_path).stem
        out_path = raw_path.parent / f"{base}_from_raw.pptx"
    out_path = Path(out_path)
    prs.save(str(out_path))
    print(f"[3] 已生成: {out_path.resolve()}")


if __name__ == "__main__":
    main()
