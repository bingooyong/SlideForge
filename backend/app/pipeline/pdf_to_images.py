from __future__ import annotations

from dataclasses import dataclass
from typing import List
import io

import fitz  # PyMuPDF
from PIL import Image


@dataclass
class PageImage:
    """
    单页 PDF 渲染结果。

    - image_bytes: PNG 编码后的字节内容（适合网络传输或落盘）
    - width / height: 渲染后图片像素尺寸
    - page_number: 1-based 页码

    默认渲染 scale=2.0 时适用于后续版面解析与坐标换算。
    """

    image_bytes: bytes
    width: int
    height: int
    page_number: int


class PDFConversionError(Exception):
    """PDF 转图片过程中发生的通用错误。"""


class EncryptedPDFError(PDFConversionError):
    """加密 PDF 未提供密码时的错误。"""


class EmptyPDFError(PDFConversionError):
    """PDF 不包含任何页面时的错误。"""


def get_pdf_page_count(pdf_path: str) -> int:
    """
    返回 PDF 的页数。

    主要用于上传端点返回 pageCount 等快速元信息，避免在该阶段就渲染整份文档。
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:  # pragma: no cover - 依赖底层库的具体异常类型
        raise PDFConversionError(f"Failed to open PDF: {exc}") from exc

    try:
        if doc.needs_pass:
            raise EncryptedPDFError("Encrypted PDF is not supported without password.")
        if doc.page_count == 0:
            raise EmptyPDFError("PDF has no pages.")
        return doc.page_count
    except PDFConversionError:
        raise
    except Exception as exc:  # pragma: no cover
        raise PDFConversionError(f"Failed to inspect PDF pages: {exc}") from exc
    finally:
        doc.close()


def get_page_thumbnail(pdf_path: str, page_index: int, scale: float = 0.4) -> bytes:
    """
    将 PDF 指定页渲染为缩略图 PNG 字节，用于前端预览。

    Args:
        pdf_path: PDF 本地路径。
        page_index: 0-based 页索引。
        scale: 渲染缩放，缩略图用较小值（如 0.4）即可。

    Returns:
        PNG 图片字节。

    Raises:
        PDFConversionError, EncryptedPDFError, EmptyPDFError, ValueError
    """
    if scale <= 0:
        raise ValueError("scale must be positive.")
    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise PDFConversionError(f"Failed to open PDF: {exc}") from exc
    try:
        if doc.needs_pass:
            raise EncryptedPDFError("Encrypted PDF is not supported without password.")
        if doc.page_count == 0:
            raise EmptyPDFError("PDF has no pages.")
        if page_index < 0 or page_index >= doc.page_count:
            raise ValueError(f"page_index {page_index} out of range [0, {doc.page_count})")
        page = doc.load_page(page_index)
        matrix = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    finally:
        doc.close()


def pdf_to_images(pdf_path: str, scale: float = 2.0) -> List[PageImage]:
    """
    将本地 PDF 文件按页渲染为 PNG 图片列表。

    Args:
        pdf_path: PDF 文件的本地路径。
        scale: 渲染缩放比例（>0），例如 2.0 表示在基础分辨率上放大 2 倍。

    Returns:
        每页对应的 PageImage 列表，按页码递增排序。

    Raises:
        ValueError: scale 非正数。
        EncryptedPDFError: PDF 被加密且未解锁。
        EmptyPDFError: PDF 页数为 0。
        PDFConversionError: 其它打开或渲染过程中的错误。
    """
    if scale <= 0:
        raise ValueError("scale must be positive.")

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:  # pragma: no cover - 依赖底层库的具体异常类型
        raise PDFConversionError(f"Failed to open PDF: {exc}") from exc

    try:
        if doc.needs_pass:
            raise EncryptedPDFError("Encrypted PDF is not supported without password.")

        if doc.page_count == 0:
            raise EmptyPDFError("PDF has no pages.")

        matrix = fitz.Matrix(scale, scale)
        images: List[PageImage] = []

        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            pix = page.get_pixmap(matrix=matrix, alpha=False)

            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")

            images.append(
                PageImage(
                    image_bytes=buffer.getvalue(),
                    width=pix.width,
                    height=pix.height,
                    page_number=page_index + 1,
                )
            )

        return images
    except PDFConversionError:
        # 已经是规范化后的错误，直接抛出
        raise
    except Exception as exc:  # pragma: no cover - 依赖底层库的具体异常类型
        raise PDFConversionError(f"Error while rendering PDF pages: {exc}") from exc
    finally:
        doc.close()


def image_path_to_page_image(image_path: str) -> PageImage:
    """
    将单张图片文件加载为 PageImage（单页），供流水线与 PDF 统一处理。

    Args:
        image_path: 图片本地路径（支持 PIL 可读格式，如 jpg/png/webp/bmp）。

    Returns:
        仅包含一页的 PageImage，page_number=1。
    """
    img = Image.open(image_path)
    img = img.convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return PageImage(
        image_bytes=buffer.getvalue(),
        width=img.width,
        height=img.height,
        page_number=1,
    )

