"""
Slide Schema V2：容器嵌套 + 相对坐标 + 扁平化属性。
完全适配大模型天然输出的合理结构，避免深层嵌套导致的解析异常。
"""

from __future__ import annotations

from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field

# bbox 归一化 [x, y, w, h]，相对父容器或页面
Bbox = List[float]


# ---------- 扁平化的富文本结构 ----------
class TextRun(BaseModel):
    text: str = ""
    font_size: Optional[float] = None  # 支持 0.035 等相对比例
    font_weight: Optional[str] = None
    color: Optional[str] = None
    font_color: Optional[str] = None  # 与 color 二选一，大模型常出 font_color
    align: Optional[str] = None


# ---------- 背景 ----------
class BackgroundGradient(BaseModel):
    type: Literal["gradient"] = "gradient"
    colors: Optional[List[str]] = None
    start_color: Optional[str] = None
    end_color: Optional[str] = None
    direction: Optional[str] = None


class SlideMetadata(BaseModel):
    aspect_ratio: str = "16:9"
    background: Optional[BackgroundGradient] = None


# ---------- 核心元素 (彻底扁平化) ----------

class TextBlockV2(BaseModel):
    type: Literal["text_block", "text_box"] = "text_box"
    id: Optional[str] = None
    bbox: Bbox
    text_runs: List[TextRun] = Field(default_factory=list)
    alignment: Optional[str] = None


class ShapeTextBoxV2(BaseModel):
    type: Literal["shape_text_box"] = "shape_text_box"
    id: Optional[str] = None
    bbox: Bbox
    fill_color: Optional[str] = None
    background_color: Optional[str] = None  # 与 fill_color 二选一
    border_color: Optional[str] = None
    border_width: Optional[float] = None
    border_radius: Optional[float] = None
    radius: Optional[float] = None  # 与 border_radius 二选一
    text_runs: List[TextRun] = Field(default_factory=list)
    alignment: Optional[str] = None


class IconTextLayoutV2(BaseModel):
    type: Literal["icon_text_layout"] = "icon_text_layout"
    id: Optional[str] = None
    bbox: Bbox
    placeholder_id: Optional[str] = None
    icon_bbox: Optional[Bbox] = None
    text_bbox: Optional[Bbox] = None
    text_runs: List[TextRun] = Field(default_factory=list)
    alignment: Optional[str] = None


class ListBlockV2(BaseModel):
    type: Literal["list_block", "list_layout"] = "list_layout"
    id: Optional[str] = None
    bbox: Bbox
    bullet_type: Optional[str] = None
    item_spacing: Optional[float] = None
    # 列表项可能是嵌套的 icon_text_layout 数组，也可能是 text_runs 数组
    items: List[Any] = Field(default_factory=list)


class GroupV2(BaseModel):
    type: Literal["group"] = "group"
    id: Optional[str] = None
    bbox: Bbox
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = None
    border_radius: Optional[float] = None
    radius: Optional[float] = None  # 与 border_radius 二选一
    shadow: Optional[Any] = None  # 兼容 boolean 或 dict
    children: List["ElementV2"] = Field(default_factory=list)


ElementV2 = Annotated[
    Union[
        TextBlockV2,
        ShapeTextBoxV2,
        IconTextLayoutV2,
        ListBlockV2,
        GroupV2,
    ],
    Field(discriminator="type"),
]
GroupV2.model_rebuild()


class SlideDocumentV2(BaseModel):
    """V2 单页文档。兼容顶层 elements 或 slide_data.elements。"""
    slide_metadata: Optional[SlideMetadata] = None
    slide_data: Optional[Any] = None  # 兼容 GLM 等输出的 slide_data 包装
    elements: List[ElementV2] = Field(default_factory=list)


# ---------- 工具函数 ----------

def _bbox_relative_to_absolute(
    child_bbox: Bbox,
    parent_x: float, parent_y: float, parent_w: float, parent_h: float,
) -> Bbox:
    if len(child_bbox) != 4:
        return [0.0, 0.0, 0.0, 0.0]
    return [
        parent_x + child_bbox[0] * parent_w,
        parent_y + child_bbox[1] * parent_h,
        child_bbox[2] * parent_w,
        child_bbox[3] * parent_h,
    ]


def _attr(elem: Any, key: str, default: Any = None) -> Any:
    """兼容 Pydantic 模型与 dict（如从 slide_data 取出的元素）。"""
    if isinstance(elem, dict):
        return elem.get(key, default)
    return getattr(elem, key, default)


def collect_text_bboxes_absolute(doc: SlideDocumentV2) -> List[Bbox]:
    """
    遍历 V2 树，收集所有「需要从背景上去除」的文字/形状区域的绝对 bbox (0-1)。
    若 elements 在 slide_data 内则从中取出；支持元素为 dict 或 Pydantic 模型。
    """
    out: List[Bbox] = []
    elements = doc.elements
    if not elements and isinstance(doc.slide_data, dict):
        elements = (doc.slide_data or {}).get("elements", [])

    def walk(elem: Any, px: float, py: float, pw: float, ph: float) -> None:
        b = _attr(elem, "bbox")
        if not b or len(b) != 4:
            return
        abs_bbox = _bbox_relative_to_absolute(b, px, py, pw, ph)
        t = _attr(elem, "type")
        if t in ("text_block", "text_box", "shape_text_box", "icon_text_layout", "list_block", "list_layout"):
            out.append(abs_bbox)
        elif t == "group":
            out.append(abs_bbox)
            for child in _attr(elem, "children", []):
                walk(child, abs_bbox[0], abs_bbox[1], abs_bbox[2], abs_bbox[3])

    for elem in elements:
        walk(elem, 0.0, 0.0, 1.0, 1.0)
    return out


def slide_document_v2_to_text_blocks_for_mask(doc: SlideDocumentV2) -> List[Any]:
    """将收集到的绝对 bbox 转为 clean_background 可用的 TextBlock 列表。"""
    from app.pipeline.layout_ocr_models import Box2D, TextBlock

    bboxes = collect_text_bboxes_absolute(doc)
    return [
        TextBlock(
            id=f"v2-mask-{i}",
            type="text",
            content="",
            box=Box2D(x=b[0], y=b[1], w=b[2], h=b[3]),
        )
        for i, b in enumerate(bboxes)
        if len(b) == 4 and b[2] > 0 and b[3] > 0
    ]
