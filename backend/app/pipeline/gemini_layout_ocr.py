"""
Gemini 版面 OCR：仅负责调用 Google Gemini API，返回原始文本。

职责单一：速率限制 + Gemini generate_content（含可选 V2 结构化输出），
不包含 GLM、解析或门面逻辑。V2 提示词与 response_schema 属于 Gemini 能力，保留于此。
"""

from __future__ import annotations

import time
from collections import deque
from threading import Lock
from typing import Any, Dict, Optional

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=FutureWarning)
    import google.generativeai as genai
from google.api_core import exceptions as gcp_exceptions

from app.config import settings
from app.pipeline.layout_ocr_models import (
    LayoutOcrApiError,
    LayoutOcrInvalidResponseError,
    parse_retry_seconds_429,
)
from app.pipeline.slide_schema_v2 import SlideDocumentV2

# 向后兼容：门面与测试仍可从本模块导入旧异常名
GeminiApiError = LayoutOcrApiError
GeminiInvalidResponseError = LayoutOcrInvalidResponseError

_GEMINI_RATE_LOCK = Lock()
_GEMINI_CALL_TIMESTAMPS: deque[float] = deque()


def _respect_gemini_rate_limit() -> None:
    max_rpm = getattr(settings, "GEMINI_MAX_RPM", 15)
    if max_rpm <= 0:
        return
    while True:
        now = time.time()
        with _GEMINI_RATE_LOCK:
            cutoff = now - 60.0
            while _GEMINI_CALL_TIMESTAMPS and _GEMINI_CALL_TIMESTAMPS[0] < cutoff:
                _GEMINI_CALL_TIMESTAMPS.popleft()
            if len(_GEMINI_CALL_TIMESTAMPS) < max_rpm:
                _GEMINI_CALL_TIMESTAMPS.append(now)
                return
            sleep_for = _GEMINI_CALL_TIMESTAMPS[0] + 60.0 - now
        if sleep_for > 0:
            time.sleep(sleep_for)
        else:
            time.sleep(60.0 / max_rpm)


def _init_gemini_model(api_key: Optional[str] = None) -> genai.GenerativeModel:
    """使用请求传入的 api_key，若未传则使用环境配置 GEMINI_API_KEY。"""
    key = (api_key or "").strip() or settings.GEMINI_API_KEY
    if not key:
        raise LayoutOcrApiError("GEMINI_API_KEY is not configured (env or request).")
    genai.configure(api_key=key)
    model_name = getattr(settings, "GEMINI_LAYOUT_MODEL", "gemini-2.5-flash")
    return genai.GenerativeModel(model_name)


def _build_prompt_v2() -> str:
    """V2 终极全场景版面解析提示词：基于绝对视觉测量与严格节点分类学，防范一切排版脑补。"""
    return """
你是一个顶级的 UI/UX 前端工程师和机器视觉测量专家。你的任务是对幻灯片进行绝对客观的「逆向工程」，拆解为结构化 JSON。

【🚨 核心心法：绝对视觉客观，拒绝语义脑补】
绝不能因为某句话是“标题”就盲目让它居中或占满全宽。看到多宽写多宽，看到靠左就写靠左！100%忠实于肉眼看到的像素排版！

【📏 坐标系与安全边界】
1. Bbox 必须为 [x, y, width, height] 相对比例 (0.0~1.0)。禁止使用 [x1, y1, x2, y2]。
2. 容器相对定位：group 内子元素的 bbox 必须相对于父容器左上角计算！
3. 安全内边距 (Padding)：子元素的 x 和 y 绝对不能为 0.0！必须留出视觉边距（如 x: 0.04），严禁文字或图标贴死父容器的物理边框！

【🎨 视觉防错与 PPTX 物理限制】
1. 字号标尺 (font_size)：主标题 ~0.045，模块副标题 ~0.035，正文/列表 ~0.025 (严禁小于0.02)。
2. 颜色对比度：深色底纹上的文字必须提取为浅色/白色 (#FFFFFF)。
3. 边框降级：PPTX 不支持单侧边框！如遇单侧彩色边框（如仅左侧有红线），一律转换为外层包裹 group 的全局 border_color 和 border_width，绝对禁止创造非标准字段！

【🧱 节点分类学 (Node Types) - 必须严格遵守并扁平化属性】
1. `group`: 容器节点。用于大卡片、线框、或包裹其他元素的色块。属性：background_color, border_color, border_width, border_radius, shadow。
2. `shape_text_box`: 带底色的独立文本块（如蓝底白字标签）。属性：fill_color, border_radius。注意：务必如实测量其真实宽度。
3. `icon_text_layout`: 带图标的段落。提供 placeholder_id (如 check, lock, database, gear) 及精确的 icon_bbox 和 text_bbox。
4. `list_block`: 项目符号列表。提供 bullet_type (如 disc)，items 必须为包含文本对象的二维数组。
5. `text_block`: 常规无底色纯文本。
6. `text_runs`: 富文本数组。切分为多个 run，包含 text, font_size, color, font_weight, align。

必须输出纯 JSON，严禁 Markdown 代码块包裹。严格参照以下包含所有组件的终极模板，绝不能自创层级：
{
  "slide_metadata": { "aspect_ratio": "16:9", "background": { "type": "gradient", "colors": ["#E6F0F6", "#F8FBFD"] } },
  "elements": [
    {
      "type": "text_block",
      "bbox": [0.05, 0.05, 0.90, 0.08],
      "text_runs": [ { "text": "Page 2 需求阶段...", "font_size": 0.045, "color": "#000000", "font_weight": "bold", "align": "left" } ]
    },
    {
      "type": "group",
      "bbox": [0.05, 0.15, 0.90, 0.58],
      "background_color": "#FFFFFF",
      "border_color": "#E04B50",
      "border_width": 2,
      "border_radius": 0.015,
      "shadow": true,
      "children": [
        {
          "type": "shape_text_box",
          "bbox": [0.03, 0.04, 0.45, 0.10],
          "fill_color": "#3471A1",
          "text_runs": [ { "text": "【能力域：安全研发要求】", "font_size": 0.038, "color": "#FFFFFF", "font_weight": "bold", "align": "center" } ]
        },
        {
          "type": "icon_text_layout",
          "bbox": [0.05, 0.20, 0.90, 0.15],
          "placeholder_id": "document_check",
          "icon_bbox": [0.00, 0.00, 0.08, 1.00],
          "text_bbox": [0.10, 0.00, 0.90, 1.00],
          "text_runs": [
            { "text": "统一规范体系 (通过) : ", "font_size": 0.028, "color": "#000000", "font_weight": "bold" },
            { "text": "汇编并执行安全规范。", "font_size": 0.028, "color": "#000000" }
          ]
        },
        {
          "type": "list_block",
          "bbox": [0.05, 0.40, 0.90, 0.25],
          "bullet_type": "disc",
          "items": [
            [ { "text": "现状：目前依赖OA通告。", "font_size": 0.026, "color": "#000000" } ],
            [ { "text": "AI数智化改进：构建AI漏洞情报图谱。", "font_size": 0.026, "color": "#000000" } ]
          ]
        }
      ]
    }
  ]
}
"""


def _get_v2_response_schema() -> Dict[str, Any]:
    """返回 V2 版面结构的 JSON Schema，用于 Gemini 结构化输出（response_schema）。"""
    return SlideDocumentV2.model_json_schema()


def _call_gemini_with_retry(
    model: genai.GenerativeModel,
    prompt: str,
    image_b64: str,
    max_retries: int = 5,
    base_delay: float = 1.0,
    generation_config: Optional[Any] = None,
) -> str:
    last_error: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            _respect_gemini_rate_limit()
            kwargs: Dict[str, Any] = {}
            if generation_config is not None:
                kwargs["generation_config"] = generation_config
            response = model.generate_content(
                [
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": image_b64,
                                }
                            },
                        ],
                    }
                ],
                **kwargs,
            )
            text = response.text
            if not text:
                raise LayoutOcrInvalidResponseError("Empty response text from Gemini.")
            return text
        except gcp_exceptions.ResourceExhausted as exc:
            last_error = exc
            if attempt == max_retries - 1:
                raise LayoutOcrApiError(
                    f"Gemini API quota exceeded after {max_retries} attempts. "
                    "Check https://ai.google.dev/gemini-api/docs/rate-limits or try another API key."
                ) from exc
            wait = parse_retry_seconds_429(exc) or 60.0
            time.sleep(wait)
        except Exception as exc:
            last_error = exc
            if attempt == max_retries - 1:
                raise LayoutOcrApiError(
                    f"Gemini API failed after {max_retries} attempts: {exc}"
                ) from exc
            time.sleep(base_delay * (2**attempt))
    raise LayoutOcrApiError(f"Gemini API failed: {last_error}")  # pragma: no cover


def call_gemini_raw(
    prompt: str,
    image_b64: str,
    generation_config: Optional[Any] = None,
    max_retries: int = 5,
    base_delay: float = 1.0,
    api_key: Optional[str] = None,
) -> str:
    """
    调用 Gemini API，返回模型输出的原始文本。
    若传入 api_key 则优先使用（界面配置），否则使用环境 GEMINI_API_KEY。

    Raises:
        LayoutOcrApiError: API 调用失败。
        LayoutOcrInvalidResponseError: 返回内容为空。
    """
    model = _init_gemini_model(api_key=api_key)
    return _call_gemini_with_retry(
        model, prompt, image_b64,
        max_retries=max_retries,
        base_delay=base_delay,
        generation_config=generation_config,
    )
