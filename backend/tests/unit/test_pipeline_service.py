"""PipelineService 单元测试（mock 各 stage 调用，验证编排与 progress 回调）。"""
from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from app.pipeline.background_cleaning import CleanedBackground
from app.pipeline.color_extraction import StyleInfo
from app.pipeline.layout_ocr_models import Box2D, Slide, TextBlock
from app.pipeline.pipeline_service import PipelineResult, PipelineService, ProgressEvent


def _make_mock_slide() -> Slide:
    return Slide(
        id="slide-1",
        index=0,
        aspectRatio="16:9",
        blocks=[
            TextBlock(id="t1", content="x", box=Box2D(x=0.1, y=0.1, w=0.2, h=0.1)),
        ],
        metadata=None,
    )


def test_pipeline_service_run_calls_progress_callback(
    minimal_pdf_path: Path,
    tmp_path: Path,
) -> None:
    """PipelineService.run 应在各阶段调用 progress_callback。"""
    events: list[ProgressEvent] = []

    def capture(event: ProgressEvent) -> None:
        events.append(event)

    with (
        patch("app.pipeline.pipeline_service.get_layout_ocr_raw_response_v2") as mock_ocr,
        patch("app.pipeline.pipeline_service.extract_colors") as mock_colors,
        patch("app.pipeline.pipeline_service.crop_imageblocks") as mock_crop,
        patch("app.pipeline.pipeline_service.clean_background") as mock_clean,
        patch("app.pipeline.pipeline_service.create_slide_v2") as mock_pptx,
    ):
        mock_ocr.return_value = '{"elements": []}'
        mock_colors.return_value = StyleInfo(
            primaryColor="#000000",
            backgroundColor="#FFFFFF",
            accentColors=["#000000"],
        )
        mock_crop.return_value = []
        buf = io.BytesIO()
        Image.new("RGB", (100, 100), (255, 255, 255)).save(buf, format="PNG")
        mock_clean.return_value = CleanedBackground(
            page_number=1,
            image_bytes=buf.getvalue(),
            width=100,
            height=100,
            method="blur",
        )
        mock_pptx.return_value = None

        service = PipelineService(default_output_root=tmp_path)
        result = service.run(
            task_id="test-task",
            pdf_path=str(minimal_pdf_path),
            progress_callback=capture,
        )

    assert isinstance(result, PipelineResult)
    assert result.task_id == "test-task"
    assert result.total_pages == 1
    assert len(events) >= 1
    assert any(e.stage in ("ocr", "colors", "cropping", "background", "pptx") for e in events)


def test_pipeline_service_degradation_one_page_fails_still_completes(
    two_page_pdf_path: Path,
    tmp_path: Path,
) -> None:
    """单页失败时调用 add_slide_degraded 占位，任务仍完成，failedPages 正确。"""
    with (
        patch("app.pipeline.pipeline_service.get_layout_ocr_raw_response_v2") as mock_ocr,
        patch("app.pipeline.pipeline_service.extract_colors") as mock_colors,
        patch("app.pipeline.pipeline_service.crop_imageblocks") as mock_crop,
        patch("app.pipeline.pipeline_service.clean_background") as mock_clean,
        patch("app.pipeline.pipeline_service.create_slide_v2") as mock_create,
        patch("app.pipeline.pipeline_service.add_slide_degraded") as mock_degraded,
    ):
        mock_degraded.return_value = None
        mock_colors.return_value = StyleInfo(
            primaryColor="#000000",
            backgroundColor="#FFFFFF",
            accentColors=["#000000"],
        )
        mock_crop.return_value = []
        buf = io.BytesIO()
        Image.new("RGB", (100, 100), (255, 255, 255)).save(buf, format="PNG")
        mock_clean.return_value = CleanedBackground(
            page_number=1,
            image_bytes=buf.getvalue(),
            width=100,
            height=100,
            method="blur",
        )

        def ocr_side_effect(page):
            if page.page_number == 2:
                raise Exception("Gemini timeout")
            return '{"elements": []}'

        mock_ocr.side_effect = ocr_side_effect
        mock_create.return_value = None

        service = PipelineService(default_output_root=tmp_path)
        result = service.run(
            task_id="degrade-task",
            pdf_path=str(two_page_pdf_path),
        )

    assert result.task_id == "degrade-task"
    assert result.total_pages == 2
    assert result.failed_pages == [1]
    assert result.output_pptx_path is not None
    assert result.output_pptx_path.exists()
    assert any(r.success for r in result.page_results)
    assert mock_create.call_count == 1
    assert mock_degraded.call_count == 1
    assert mock_degraded.call_args[0][1].page_number == 2
