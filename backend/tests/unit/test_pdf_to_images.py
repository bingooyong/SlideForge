"""pdf_to_images 与 get_pdf_page_count 单元测试。"""
from __future__ import annotations

import pytest

from app.pipeline.pdf_to_images import (
    EmptyPDFError,
    EncryptedPDFError,
    PDFConversionError,
    PageImage,
    get_pdf_page_count,
    pdf_to_images,
)


def test_get_pdf_page_count(minimal_pdf_path: str) -> None:
    """有效单页 PDF 应返回页数 1。"""
    assert get_pdf_page_count(str(minimal_pdf_path)) == 1


def test_get_pdf_page_count_nonexistent() -> None:
    """不存在路径应抛出 PDFConversionError。"""
    with pytest.raises(PDFConversionError):
        get_pdf_page_count("/nonexistent/path.pdf")


def test_pdf_to_images_returns_list_of_page_image(minimal_pdf_path: str) -> None:
    """pdf_to_images 应返回 PageImage 列表。"""
    result = pdf_to_images(str(minimal_pdf_path))
    assert len(result) == 1
    page = result[0]
    assert isinstance(page, PageImage)
    assert page.page_number == 1
    assert page.width > 0 and page.height > 0
    assert len(page.image_bytes) > 0


def test_pdf_to_images_invalid_scale(minimal_pdf_path: str) -> None:
    """scale <= 0 应抛出 ValueError。"""
    with pytest.raises(ValueError, match="scale must be positive"):
        pdf_to_images(str(minimal_pdf_path), scale=0)
    with pytest.raises(ValueError, match="scale must be positive"):
        pdf_to_images(str(minimal_pdf_path), scale=-1.0)


def test_pdf_to_images_nonexistent() -> None:
    """不存在文件应抛出 PDFConversionError。"""
    with pytest.raises(PDFConversionError):
        pdf_to_images("/nonexistent/file.pdf")
