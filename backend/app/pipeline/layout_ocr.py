"""
版面 OCR 门面：按配置选择 Gemini 或 GLM，统一提供 analyze_layout / analyze_layout_v2 等入口。

职责：根据 LAYOUT_OCR_PROVIDER 调度后端、构建提示词、解析 JSON，不实现具体 API 调用。
下游与测试应从此模块或 layout_ocr_models 导入类型与异常，避免依赖 gemini_layout_ocr 的实现细节。
"""

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import ValidationError

from app.config import settings
from app.pipeline.gemini_layout_ocr import (
    _build_prompt_v2,
    _get_v2_response_schema,
    call_gemini_raw,
)
from app.pipeline.glm_layout_ocr import build_prompt_v2_glm, call_glm_raw
from app.pipeline.layout_ocr_models import (
    Box2D,
    GeminiApiError,
    GeminiInvalidResponseError,
    ImageBlock,
    Slide,
    SlideMetadata,
    TextBlock,
    build_prompt_v1,
    encode_image_to_b64,
    parse_slide_json,
    strip_markdown_json,
)
from app.pipeline.pdf_to_images import PageImage


def _current_provider() -> str:
    return (getattr(settings, "LAYOUT_OCR_PROVIDER", "gemini") or "gemini").strip().lower()


def get_layout_ocr_raw_response(page_image: PageImage) -> str:
    """
    仅调用大模型，返回其原始文本输出（不做 JSON 解析与校验）。
    使用 V1 提示词，后端由 LAYOUT_OCR_PROVIDER 决定。
    """
    prompt = build_prompt_v1()
    image_b64 = encode_image_to_b64(page_image.image_bytes)
    if _current_provider() == "glm":
        return call_glm_raw(prompt, image_b64)
    return call_gemini_raw(prompt, image_b64)


def analyze_layout(page_image: PageImage) -> Slide:
    """
    对单页图片调用配置的版面 OCR 后端（Gemini 或智谱 GLM），返回符合 Slide Schema 的结构化结果。
    """
    prompt = build_prompt_v1()
    image_b64 = encode_image_to_b64(page_image.image_bytes)
    provider = _current_provider()

    if provider == "glm":
        raw_text = call_glm_raw(prompt, image_b64)
    else:
        raw_text = call_gemini_raw(prompt, image_b64)

    raw_json = parse_slide_json(raw_text)
    try:
        slide = Slide.model_validate(raw_json)
    except ValidationError as exc:
        raise GeminiInvalidResponseError(f"Slide schema validation failed: {exc}") from exc

    parsed_blocks: List[Any] = []
    for block in slide.blocks:
        if isinstance(block, dict):
            btype = block.get("type")
            try:
                if btype == "text":
                    parsed_blocks.append(TextBlock.model_validate(block))
                elif btype == "image":
                    parsed_blocks.append(ImageBlock.model_validate(block))
                else:
                    continue
            except ValidationError:
                continue
        else:
            parsed_blocks.append(block)
    slide.blocks = parsed_blocks

    if slide.metadata is None:
        slide.metadata = SlideMetadata(sourcePage=page_image.page_number, mode="standard")
    elif slide.metadata.sourcePage is None:
        slide.metadata.sourcePage = page_image.page_number

    return slide


def get_layout_ocr_raw_response_v2(
    page_image: PageImage,
    use_structured_output: Optional[bool] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    使用 V2 提示词（+ 可选结构化输出）调用大模型，返回原始文本，不做解析。
    GLM 无 response_schema，使用专用硬模板提示词（build_prompt_v2_glm）约束 bbox 与结构。
    api_key: 可选，界面或请求传入的 Gemini API Key，未传则使用环境配置。
    """
    image_b64 = encode_image_to_b64(page_image.image_bytes)
    provider = _current_provider()
    if use_structured_output is None:
        use_structured_output = getattr(settings, "LAYOUT_OCR_V2_STRUCTURED_OUTPUT", True)

    if provider == "glm":
        prompt = build_prompt_v2_glm()
        return call_glm_raw(prompt, image_b64)

    prompt = _build_prompt_v2()

    if use_structured_output:
        try:
            import google.generativeai as genai
            config = genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=_get_v2_response_schema(),
            )
            return call_gemini_raw(prompt, image_b64, generation_config=config, api_key=api_key)
        except Exception:
            return call_gemini_raw(prompt, image_b64, api_key=api_key)
    return call_gemini_raw(prompt, image_b64, api_key=api_key)


def _normalize_page_elements_to_elements(raw: dict) -> None:
    """
    兼容 Gemini 结构化输出等返回的 page_elements 根键：转为 elements，并抽出首项 background 到 slide_metadata.background。
    """
    pe = raw.get("page_elements")
    if not isinstance(pe, list) or "elements" in raw:
        return
    elements: List[Any] = []
    for e in pe:
        if isinstance(e, dict) and e.get("type") == "background":
            bg = e.get("background_gradient") or e
            if isinstance(bg, dict):
                colors = bg.get("colors")
                meta = raw.setdefault("slide_metadata", {})
                if not isinstance(meta, dict):
                    meta = {}
                    raw["slide_metadata"] = meta
                meta["background"] = {
                    "type": "gradient",
                    "colors": colors,
                    "start_color": bg.get("start_color") or (colors[0] if colors else None),
                    "end_color": bg.get("end_color") or (colors[-1] if colors and len(colors) > 1 else None),
                    "direction": bg.get("direction"),
                }
        else:
            elements.append(e)
    raw["elements"] = elements
    del raw["page_elements"]


def parse_layout_v2_raw(raw_text: str) -> Any:
    """
    将 V2 大模型原始输出字符串解析为可用于渲染的 dict（保留 content/runs 等，供 create_slide_v2 出文字）。
    兼容根键 page_elements。始终返回 dict，与 scripts/run_pptx_from_raw.py 解析结果一致，便于统一调试。
    注意：不在此处调用 normalize_glm_v2_output，因 Gemini 输出已是相对坐标，归一化会破坏子元素 bbox 导致内容错位/重叠。
    """
    text = strip_markdown_json(raw_text)
    raw_json = parse_slide_json(text)
    if not isinstance(raw_json, dict):
        raise GeminiInvalidResponseError("parse_layout_v2_raw: parsed result is not a dict")
    _normalize_page_elements_to_elements(raw_json)
    return raw_json


def analyze_layout_v2(
    page_image: PageImage,
    use_structured_output: Optional[bool] = None,
) -> Any:
    """
    使用 V2 提示词（容器嵌套 + 相对坐标）对单页图片做版面解析。
    返回 SlideDocumentV2 或 dict（含 slide_data.elements），供 create_slide_v2 渲染；
    大模型若输出 slide_data / text_box / text_runs 等格式，会以 dict 返回以兼容渲染层。
    """
    raw_text = get_layout_ocr_raw_response_v2(page_image, use_structured_output=use_structured_output)
    return parse_layout_v2_raw(raw_text)
