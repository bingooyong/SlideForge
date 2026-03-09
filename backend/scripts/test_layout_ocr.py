#!/usr/bin/env python3
"""
用单张图片测试版面 OCR（Gemini 或智谱 GLM）。

用法（在 backend 目录下）:
  # V1：只调大模型，保存原始输出
  python scripts/test_layout_ocr.py --raw [图片路径]
  # V1：调大模型 + 解析为 Slide JSON（扁平 blocks）
  python scripts/test_layout_ocr.py [图片路径]

  # V2（容器嵌套 + 富文本）：只保存原始输出，便于对比是否出现 group/富文本
  python scripts/test_layout_ocr.py --v2 --raw [图片路径]
  # V2：调大模型 + 解析为 SlideDocumentV2 JSON
  python scripts/test_layout_ocr.py --v2 [图片路径]

  # 测试时缩小图片以加快请求（如 GLM 视觉模型较慢时可试）
  python scripts/test_layout_ocr.py --raw --max-size 1280

  默认图片: ../assets/demo-001.jpg
  依赖 .env 中的 LAYOUT_OCR_PROVIDER 与对应 API Key。V2 时 Gemini 可配 LAYOUT_OCR_V2_STRUCTURED_OUTPUT=true 启用 JSON Schema 约束。
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path

# 保证能 import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from app.config import settings
from app.pipeline.layout_ocr import (
    GeminiApiError,
    GeminiInvalidResponseError,
    analyze_layout,
    analyze_layout_v2,
    get_layout_ocr_raw_response,
    get_layout_ocr_raw_response_v2,
)
from app.pipeline.pdf_to_images import PageImage


def _model_label_for_filename() -> str:
    """当前配置的 provider + model，用于文件名（便于对比不同模型输出）。"""
    provider = (getattr(settings, "LAYOUT_OCR_PROVIDER", "gemini") or "gemini").strip().lower()
    if provider == "glm":
        model = getattr(settings, "GLM_LAYOUT_MODEL", "glm-4v-plus") or "glm-4v-plus"
    else:
        model = getattr(settings, "GEMINI_LAYOUT_MODEL", "gemini-2.5-flash") or "gemini-2.5-flash"
    # 文件名安全：去掉或替换不友好字符
    safe = f"{provider}_{model}".replace(".", "_")
    return safe


def load_page_image(image_path: Path, max_size: int | None = None) -> PageImage:
    """从本地图片文件加载为 PageImage（统一转为 PNG 字节）。max_size 为最长边上限（像素），可缩小体积以加快 GLM 等请求。"""
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        w, h = img.size
        if max_size and max(w, h) > max_size:
            ratio = max_size / max(w, h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            w, h = new_w, new_h
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
    return PageImage(image_bytes=image_bytes, width=w, height=h, page_number=1)


def run_raw_only(image_path: Path, page_image: PageImage, v2: bool = False) -> None:
    """只调大模型，把原始输出写到文件，便于先验证大模型输出是否正确。"""
    model_label = _model_label_for_filename()
    suffix = "_v2" if v2 else ""
    raw_path = image_path.parent / f"{image_path.stem}_llm_raw_{model_label}{suffix}.txt"
    print(f"加载图片: {image_path}", flush=True)
    print(f"尺寸: {page_image.width} x {page_image.height}", flush=True)
    print(f"当前模型: {model_label} (V2={v2})", flush=True)
    print("调用大模型（仅取原始文本，不做解析）...", flush=True)
    print("请求中（连接超时 15s，读取超时 90s，请稍候）...", flush=True)
    t0 = time.monotonic()
    try:
        raw_text = (
            get_layout_ocr_raw_response_v2(page_image)
            if v2
            else get_layout_ocr_raw_response(page_image)
        )
    except GeminiApiError as e:
        print(f"API 错误: {e}", file=sys.stderr)
        sys.exit(2)
    elapsed = time.monotonic() - t0
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(raw_text)
    print(f"大模型原始输出已写入: {raw_path}", file=sys.stderr)
    print(f"长度: {len(raw_text)} 字符，耗时: {elapsed:.1f}s", file=sys.stderr)
    # 在 stdout 打出前 500 字符，方便快速目视
    preview = raw_text[:500] + ("..." if len(raw_text) > 500 else "")
    print("\n--- 原始输出预览（前 500 字符）---")
    print(preview)


def run_full(image_path: Path, page_image: PageImage, v2: bool = False) -> None:
    """调大模型 + 解析为 Slide(V1) 或 SlideDocumentV2(V2)，输出结构化 JSON。"""
    model_label = _model_label_for_filename()
    suffix = "_v2" if v2 else ""
    print(f"加载图片: {image_path}", flush=True)
    print(f"尺寸: {page_image.width} x {page_image.height}, 当前模型: {model_label} (V2={v2})", flush=True)
    print("调用版面 OCR（含解析）...", flush=True)
    t0 = time.monotonic()
    try:
        if v2:
            doc = analyze_layout_v2(page_image)
            out = doc.model_dump(mode="json")
        else:
            slide = analyze_layout(page_image)
            out = slide.model_dump(mode="json")
    except GeminiApiError as e:
        print(f"API 错误: {e}", file=sys.stderr)
        sys.exit(2)
    except GeminiInvalidResponseError as e:
        print(f"解析错误: {e}", file=sys.stderr)
        sys.exit(3)
    elapsed = time.monotonic() - t0
    print(json.dumps(out, ensure_ascii=False, indent=2))
    out_path = image_path.parent / f"{image_path.stem}_layout_{model_label}{suffix}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n已写入: {out_path}，耗时: {elapsed:.1f}s", file=sys.stderr)


def main() -> None:
    default_image = Path(__file__).resolve().parent.parent.parent / "assets" / "demo-001.jpg"
    parser = argparse.ArgumentParser(
        description="测试版面 OCR：--raw 仅保存大模型原始输出，默认则解析为 Slide JSON"
    )
    parser.add_argument(
        "image_path",
        nargs="?",
        default=default_image,
        type=Path,
        help=f"图片路径，默认 {default_image}",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="只调大模型并保存原始输出到 <原名>_llm_raw[_v2].txt，不解析",
    )
    parser.add_argument(
        "--v2",
        action="store_true",
        default=True,
        help="使用 V2 提示词与结构（group/富文本/容器嵌套），默认开启",
    )
    parser.add_argument(
        "--v1",
        action="store_true",
        help="使用 V1 扁平结构（关闭 V2）",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=None,
        metavar="N",
        help="测试时将图片最长边缩放到 N 像素（如 1280），减小请求体积、加快 GLM 等视觉模型响应",
    )
    args = parser.parse_args()
    image_path = args.image_path

    if not image_path.is_file():
        print(f"文件不存在: {image_path}", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    page_image = load_page_image(image_path, max_size=args.max_size)
    if args.max_size is not None:
        print(f"已按 --max-size {args.max_size} 缩放，当前尺寸: {page_image.width} x {page_image.height}", file=sys.stderr)
    use_v2 = args.v2 and not args.v1
    if args.raw:
        run_raw_only(image_path, page_image, v2=use_v2)
    else:
        run_full(image_path, page_image, v2=use_v2)


if __name__ == "__main__":
    main()
