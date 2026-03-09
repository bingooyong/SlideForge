#!/usr/bin/env python3
"""
验证 Schema V2：解析 JSON → 收集 bbox → 转 TextBlock 蒙版 → 生成 PPTX。

用法（在 backend 目录下）:
  # 使用内置示例数据，生成纯色背景的 PPTX
  python scripts/verify_schema_v2.py

  # 使用指定图片做背景（会先做背景净化，用 V2 的 bbox 做文字蒙版）
  python scripts/verify_schema_v2.py --image ../assets/demo-001.jpg

输出:
  - 控制台打印 bbox 数量、TextBlock 数量
  - 当前目录生成 verify_schema_v2_out.pptx
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptx import Presentation

from app.pipeline.slide_schema_v2 import (
    SlideDocumentV2,
    collect_text_bboxes_absolute,
    slide_document_v2_to_text_blocks_for_mask,
)
from app.pipeline.pptx_composition import setup_slide_size
from app.pipeline.pptx_composition_v2 import create_slide_v2
from app.pipeline.background_cleaning import clean_background
from app.pipeline.pdf_to_images import PageImage


def _minimal_v2_doc() -> dict:
    """返回一份最小可用的 V2 示例（扁平化：text_runs、fill_color、background_color）。"""
    return {
        "slide_metadata": {"aspect_ratio": "16:9"},
        "elements": [
            {
                "type": "text_box",
                "id": "main_title",
                "bbox": [0.05, 0.05, 0.90, 0.10],
                "text_runs": [
                    {
                        "text": "Page 1 需求阶段：安全门限与权限管控",
                        "font_size": 0.04,
                        "font_weight": "bold",
                        "color": "#000000",
                    }
                ],
            },
            {
                "type": "group",
                "id": "left_card",
                "bbox": [0.05, 0.18, 0.43, 0.75],
                "background_color": "#FFFFFF",
                "border_radius": 0.015,
                "children": [
                    {
                        "type": "shape_text_box",
                        "id": "left_header",
                        "bbox": [0.02, 0.03, 0.96, 0.12],
                        "fill_color": "#4A77A8",
                        "border_radius": 0.008,
                        "text_runs": [
                            {
                                "text": "【能力域：设立安全门限要求】",
                                "color": "#FFFFFF",
                                "font_weight": "bold",
                                "align": "center",
                            }
                        ],
                    },
                    {
                        "type": "icon_text_layout",
                        "id": "left_item_1",
                        "bbox": [0.05, 0.20, 0.90, 0.25],
                        "placeholder_id": "icon_check_1",
                        "text_runs": [
                            {"text": "全面覆盖 (通过): ", "font_weight": "bold", "color": "#333333"},
                            {"text": "已建立针对 CA 产品的项目级合规安全门限要求。", "font_weight": "normal", "color": "#333333"},
                        ],
                    },
                    {
                        "type": "group",
                        "id": "left_sub_box_red",
                        "bbox": [0.05, 0.50, 0.90, 0.45],
                        "background_color": "#FCF9F9",
                        "border_color": "#990000",
                        "border_width": 0.002,
                        "children": [
                            {
                                "type": "text_box",
                                "bbox": [0.05, 0.05, 0.90, 0.15],
                                "text_runs": [
                                    {"text": "语言基线 (部分通过)", "font_weight": "bold", "color": "#990000"}
                                ],
                            },
                            {
                                "type": "list_layout",
                                "bbox": [0.05, 0.25, 0.90, 0.70],
                                "bullet_type": "disc",
                                "items": [
                                    [{"text": "现状：具备 Go、Java、C 等语言安全规范。"}],
                                    [{"text": "AI 数智化改进：引入 AI 代码助手。"}],
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                "type": "group",
                "id": "right_card",
                "bbox": [0.52, 0.18, 0.43, 0.75],
                "background_color": "#FFFFFF",
                "border_radius": 0.015,
                "children": [
                    {
                        "type": "shape_text_box",
                        "id": "right_header",
                        "bbox": [0.02, 0.03, 0.96, 0.12],
                        "fill_color": "#4A77A8",
                        "border_radius": 0.008,
                        "text_runs": [
                            {
                                "text": "【能力域：项目角色及权限管控】",
                                "color": "#FFFFFF",
                                "font_weight": "bold",
                                "align": "center",
                            }
                        ],
                    },
                    {
                        "type": "icon_text_layout",
                        "bbox": [0.05, 0.20, 0.90, 0.30],
                        "placeholder_id": "icon_check_2",
                        "text_runs": [
                            {"text": "最小权限原则 (通过): ", "font_weight": "bold"},
                            {"text": "Git/SVN/WIKI 由配置管理员基于工单审批管控。", "font_weight": "normal"},
                        ],
                    },
                ],
            },
        ],
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="验证 Schema V2：bbox 收集 + 蒙版转换 + PPTX 生成")
    parser.add_argument("--image", type=str, default=None, help="可选：背景图片路径，不传则用生成的纯色图")
    parser.add_argument("-o", "--output", type=str, default="verify_schema_v2_out.pptx", help="输出 PPTX 路径")
    args = parser.parse_args()

    doc_dict = _minimal_v2_doc()
    doc = SlideDocumentV2.model_validate(doc_dict)

    # 1) bbox 收集
    bboxes = collect_text_bboxes_absolute(doc)
    print(f"[1] collect_text_bboxes_absolute: {len(bboxes)} bboxes")

    # 2) 转 TextBlock 供蒙版
    text_blocks = slide_document_v2_to_text_blocks_for_mask(doc)
    print(f"[2] slide_document_v2_to_text_blocks_for_mask: {len(text_blocks)} TextBlocks")

    # 3) 背景：图片 or 纯色
    if args.image:
        path = Path(args.image)
        if not path.is_file():
            print(f"错误: 图片不存在 {path}", file=sys.stderr)
            sys.exit(1)
        from PIL import Image
        with Image.open(path) as img:
            img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            page_image = PageImage(image_bytes=buf.getvalue(), width=img.width, height=img.height, page_number=1)
        cleaned = clean_background(page_image, text_blocks=text_blocks)
        print(f"[3] 背景: 使用 {path} 经 clean_background 净化")
    else:
        import numpy as np
        arr = np.ones((360, 640, 3), dtype=np.uint8)
        arr[:, :] = [232, 244, 253]  # 浅蓝
        buf = io.BytesIO()
        from PIL import Image
        Image.fromarray(arr).save(buf, format="PNG")
        page_image = PageImage(image_bytes=buf.getvalue(), width=640, height=360, page_number=1)
        cleaned = clean_background(page_image, text_blocks=[])
        print("[3] 背景: 纯色 640x360")

    # 4) 生成 PPTX
    prs = Presentation()
    setup_slide_size(prs, "16:9")
    create_slide_v2(prs, doc, cleaned, icon_images=None)
    out_path = Path(args.output)
    prs.save(str(out_path))
    print(f"[4] 已生成: {out_path.resolve()}")


if __name__ == "__main__":
    main()
