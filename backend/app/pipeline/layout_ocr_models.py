"""
版面 OCR 共享模型与工具：Slide/TextBlock/ImageBlock 等 V1 结构、异常、JSON 解析与 V1 提示词。

供 layout_ocr（门面）、gemini_layout_ocr、glm_layout_ocr 及下游 pipeline 使用。
单一数据源，符合单一职责：本模块只负责「契约与解析」，不负责具体 API 调用。
"""

from __future__ import annotations

import base64
import json
import re
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ValidationError, confloat


class LayoutOcrApiError(Exception):
    """版面 OCR API 调用失败（网络、鉴权、限流等），任一后端均抛出此异常。"""


class LayoutOcrInvalidResponseError(Exception):
    """版面 OCR 返回内容无法解析为期望的 JSON 结构。"""


# 向后兼容：保留旧名
GeminiApiError = LayoutOcrApiError
GeminiInvalidResponseError = LayoutOcrInvalidResponseError


class Box2D(BaseModel):
    x: confloat(ge=0, le=1)
    y: confloat(ge=0, le=1)
    w: confloat(ge=0, le=1)
    h: confloat(ge=0, le=1)


class TextStyle(BaseModel):
    fontSize: float = Field(..., ge=1)
    fontWeight: Optional[str] = Field(
        default=None, pattern="^(normal|bold|lighter|bolder)$"
    )
    fontColor: Optional[str] = Field(
        default=None, pattern="^#[0-9A-Fa-f]{6}$"
    )
    textAlign: Optional[str] = Field(
        default="left", pattern="^(left|center|right|justify)$"
    )
    verticalAlign: Optional[str] = Field(
        default="top", pattern="^(top|middle|bottom)$"
    )


class TextBlock(BaseModel):
    id: str
    type: Literal["text"] = "text"
    content: str
    box: Box2D
    style: Optional[TextStyle] = None
    zIndex: int = 1


class ImageBlock(BaseModel):
    id: str
    type: Literal["image"] = "image"
    resourceType: str = Field("id", pattern="^(id|base64|url)$")
    resource: str
    box: Box2D
    opacity: float = Field(1.0, ge=0, le=1)
    zIndex: int = 0


class SlideMetadata(BaseModel):
    sourcePage: Optional[int] = None
    mode: Optional[str] = Field(default="standard", pattern="^(lite|standard)$")
    ocrConfidence: Optional[float] = Field(default=None, ge=0, le=1)


class Slide(BaseModel):
    id: str
    index: int
    aspectRatio: str = Field("16:9", pattern="^(16:9|9:16|4:3)$")
    blocks: List[Any]
    metadata: Optional[SlideMetadata] = None


def encode_image_to_b64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("ascii")


def parse_retry_seconds_429(exc: Exception) -> Optional[float]:
    """从 429 错误信息中解析 API 建议的重试等待秒数。"""
    msg = str(exc)
    m = re.search(r"retry in ([\d.]+)\s*s", msg, re.IGNORECASE)
    if m:
        return min(float(m.group(1)), 120.0)
    m = re.search(r"seconds:\s*(\d+)", msg)
    if m:
        return min(float(m.group(1)), 120.0)
    return None


def parse_slide_json(raw_text: str) -> Dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw_text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise LayoutOcrInvalidResponseError(f"Response is not valid JSON: {exc}") from exc


def strip_markdown_json(raw: str) -> str:
    """去掉可能的 Markdown 代码块包裹，只保留纯 JSON 字符串。"""
    s = raw.strip()
    if s.startswith("```"):
        first = s.find("\n")
        if first != -1:
            s = s[first + 1 :]
        if s.endswith("```"):
            s = s[: s.rfind("```")].strip()
    return s


def build_prompt_v1() -> str:
    """V1 版面 OCR 提示词（扁平 blocks），Gemini 与 GLM 共用。"""
    return """
你是一个版面分析和 OCR 专家。现在给你一张 PPT 页的截图，请根据图片内容返回一个 JSON，描述该页的**所有**文本块和图片块。

重要：必须识别并输出**所有**文字区域，包括：
- 标题、正文、卡片/白框内的文字（content 填识别出的文字，用于最终 PPT 可编辑文本）；
- **右下角或四角的水印、角标、Logo 旁小字**（每个水印区域单独一个 text 块，box 框住整块水印，content 可填 "水印" 或实际文字）；
- **斜角、半透明、或叠在画面上的装饰性/覆盖文字**（每个连续区域一个 text 块，box 框住该区域，content 可填实际内容或 "装饰文字"）。
以上所有文字区域的 box 都会用于背景净化（从背景图上去除这些区域），因此 box 的坐标和宽高必须准确、完整覆盖该处文字。

严格按照下面的 JSON 结构输出（不要包含多余文字、解释或注释，只输出 JSON 对象）：

{
  "id": "slide-1",
  "index": 0,
  "aspectRatio": "16:9",
  "blocks": [
    {
      "id": "text-1",
      "type": "text",
      "content": "主标题文本",
      "box": { "x": 0.1, "y": 0.1, "w": 0.8, "h": 0.15 },
      "style": {
        "fontSize": 32,
        "fontWeight": "bold",
        "fontColor": "#000000",
        "textAlign": "center",
        "verticalAlign": "middle"
      },
      "zIndex": 1
    },
    {
      "id": "image-1",
      "type": "image",
      "resourceType": "id",
      "resource": "image-1",
      "box": { "x": 0.1, "y": 0.3, "w": 0.3, "h": 0.3 },
      "opacity": 1.0,
      "zIndex": 0
    }
  ],
  "metadata": {
    "sourcePage": 1,
    "mode": "standard",
    "ocrConfidence": 0.9
  }
}

规范要求：
- 坐标和宽高使用 0-1 之间的小数，分别相对于整张幻灯片的宽和高（而不是像素）。
- blocks 中包含所有 text 与 image 块；每个可见文字区域（含水印、覆盖字）都必须有对应 text 块及准确 box。
- 对于无法确定的样式字段（例如精确字号、颜色），可以做合理估计，但不要省略必须字段。
"""
