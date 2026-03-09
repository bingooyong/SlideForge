#!/usr/bin/env python3
"""
将 PPTX 导出为图片（每页一张 PNG），依赖 LibreOffice 命令行。

用法（在 backend 目录下）:
  python scripts/pptx_to_images.py ../assets/demo-003_from_raw.pptx -o ../assets/
  python scripts/pptx_to_images.py path/to/file.pptx

不指定 -o 时，图片输出到 PPTX 所在目录。
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def _find_libreoffice() -> str | None:
    """优先使用系统 PATH 中的 libreoffice/soffice，其次 macOS 常见路径。"""
    for name in ("libreoffice", "soffice"):
        cmd = shutil.which(name)
        if cmd:
            return cmd
    # macOS 常见安装路径
    mac_path = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    if mac_path.is_file():
        return str(mac_path)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将 PPTX 导出为 PNG 图片（每页一张）",
        epilog="依赖: LibreOffice (libreoffice --headless --convert-to png)",
    )
    parser.add_argument(
        "pptx",
        type=Path,
        help="输入的 PPTX 文件路径",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        metavar="DIR",
        help="输出目录，默认与 PPTX 同目录",
    )
    args = parser.parse_args()

    pptx_path = args.pptx.resolve()
    if not pptx_path.is_file():
        print(f"错误: 未找到文件 {pptx_path}", file=sys.stderr)
        return 1

    out_dir = (args.output or pptx_path.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    lo = _find_libreoffice()
    if not lo:
        print(
            "错误: 未找到 LibreOffice。请安装 LibreOffice 并确保 'libreoffice' 在 PATH 中，"
            "或 macOS 安装于 /Applications/LibreOffice.app",
            file=sys.stderr,
        )
        return 2

    try:
        subprocess.run(
            [
                lo,
                "--headless",
                "--convert-to",
                "png",
                "--outdir",
                str(out_dir),
                str(pptx_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"错误: LibreOffice 转换失败: {e.stderr or e}", file=sys.stderr)
        return 3

    # 输出文件名为 <pptx_stem>_1.png, _2.png, ...
    stem = pptx_path.stem
    generated = sorted(out_dir.glob(f"{stem}_*.png"))
    if generated:
        print(f"已导出 {len(generated)} 张图片到 {out_dir}:")
        for p in generated:
            print(f"  {p.name}")
    else:
        print(f"已运行 LibreOffice 转换，输出目录: {out_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
