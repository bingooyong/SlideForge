"""颜色提取 extract_colors 单元测试。"""
from __future__ import annotations

import pytest

from app.pipeline.color_extraction import ColorExtractionError, StyleInfo, extract_colors

pytestmark = pytest.mark.slow
from app.pipeline.pdf_to_images import PageImage


def test_extract_colors_returns_style_info(sample_page_image: PageImage) -> None:
    """extract_colors 应返回 StyleInfo，含 primaryColor、backgroundColor、accentColors。"""
    result = extract_colors(sample_page_image, k=2, sample_size=100)
    assert isinstance(result, StyleInfo)
    assert result.primaryColor.startswith("#")
    assert result.backgroundColor.startswith("#")
    assert len(result.accentColors) >= 1


def test_extract_colors_invalid_k(sample_page_image: PageImage) -> None:
    """k <= 0 应抛出 ValueError。"""
    with pytest.raises(ValueError, match="k must be positive"):
        extract_colors(sample_page_image, k=0)
