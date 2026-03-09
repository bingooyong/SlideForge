"""版面 OCR analyze_layout 单元测试（mock API，不发起真实调用）。"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.pipeline.layout_ocr import (
    GeminiApiError,
    GeminiInvalidResponseError,
    analyze_layout,
)
from app.pipeline.layout_ocr_models import ImageBlock, Slide, TextBlock
from app.pipeline.pdf_to_images import PageImage


def test_analyze_layout_returns_slide_when_mock_returns_valid_json(
    sample_page_image: PageImage,
    sample_slide_json: dict,
) -> None:
    """当 mock 返回有效 Slide JSON 时，analyze_layout 应解析为 Slide。"""
    valid_json_str = '{"id":"slide-1","index":0,"aspectRatio":"16:9","blocks":[{"id":"text-1","type":"text","content":"Test","box":{"x":0.1,"y":0.1,"w":0.8,"h":0.15},"zIndex":1},{"id":"img-1","type":"image","resourceType":"id","resource":"img-1","box":{"x":0.2,"y":0.3,"w":0.3,"h":0.3},"opacity":1.0,"zIndex":0}],"metadata":{"sourcePage":1,"mode":"standard"}}'
    with patch("app.pipeline.layout_ocr.call_gemini_raw", return_value=valid_json_str):
        result = analyze_layout(sample_page_image)

    assert isinstance(result, Slide)
    assert result.id == "slide-1"
    assert len(result.blocks) >= 1


def test_analyze_layout_raises_on_invalid_json(sample_page_image: PageImage) -> None:
    """当 mock 返回非 JSON 时，应抛出 GeminiInvalidResponseError。"""
    with patch("app.pipeline.layout_ocr.call_gemini_raw", return_value="not valid json at all"):
        with pytest.raises(GeminiInvalidResponseError):
            analyze_layout(sample_page_image)


def test_analyze_layout_raises_on_api_error(sample_page_image: PageImage) -> None:
    """当 API 调用失败时，应抛出 GeminiApiError。"""
    with patch(
        "app.pipeline.layout_ocr.call_gemini_raw",
        side_effect=GeminiApiError("API failed"),
    ):
        with pytest.raises(GeminiApiError):
            analyze_layout(sample_page_image)


def test_analyze_layout_uses_glm_when_provider_is_glm(
    sample_page_image: PageImage,
) -> None:
    """当 LAYOUT_OCR_PROVIDER=glm 时，应调用 GLM 而非 Gemini，并返回 Slide。"""
    valid_glm_response = '{"id":"slide-1","index":0,"aspectRatio":"16:9","blocks":[{"id":"text-1","type":"text","content":"GLM","box":{"x":0.1,"y":0.1,"w":0.8,"h":0.15},"zIndex":1}],"metadata":{"sourcePage":1,"mode":"standard"}}'
    with (
        patch("app.pipeline.layout_ocr._current_provider", return_value="glm"),
        patch("app.pipeline.layout_ocr.call_glm_raw", return_value=valid_glm_response) as mock_glm,
    ):
        result = analyze_layout(sample_page_image)

    mock_glm.assert_called_once()
    assert isinstance(result, Slide)
    assert result.id == "slide-1"
    assert any(
        getattr(b, "content", None) == "GLM" for b in result.blocks
    )
