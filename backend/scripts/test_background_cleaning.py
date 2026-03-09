#!/usr/bin/env python3
"""
用单张图片测试背景净化（去水印 + 覆盖文字），不经过 PDF/LLM。

用法（在 backend 目录下）:
  python scripts/test_background_cleaning.py <图片路径>
  python scripts/test_background_cleaning.py /path/to/slide.png

输出: 同目录下生成 <原名>_cleaned.png
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

# 保证能 import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from app.pipeline.background_cleaning import clean_background
from app.pipeline.pdf_to_images import PageImage


def main() -> None:
    if len(sys.argv) != 2:
        print("用法: python scripts/test_background_cleaning.py <图片路径>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    with Image.open(path) as img:
        img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        w, h = img.size

    page_image = PageImage(image_bytes=image_bytes, width=w, height=h, page_number=1)
    # 不传 OCR 结果，只测试角区水印 + 覆盖文字检测
    result = clean_background(page_image, text_blocks=[])
    out_path = path.parent / f"{path.stem}_cleaned.png"
    with open(out_path, "wb") as f:
        f.write(result.image_bytes)
    print(f"已生成: {out_path} (method={result.method})")


if __name__ == "__main__":
    main()
