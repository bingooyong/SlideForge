"""
GLM V2 输出清洗：在无 response_schema 时，将 GLM 返回的 JSON 转为可渲染结构。

- BBox：将 [x_min, y_min, x_max, y_max] 转为 [x, y, width, height]（启发式：若 x+第三项或 y+第四项>1.01 则按对角坐标处理）。
- 结构：page -> slide_data；扁平化 style 到元素/run 顶层；list_item 转为 text_box。
- 坐标：将 GLM 输出的全局绝对坐标递归换算为相对父容器的坐标，供 pptx_composition_v2 使用。
"""

from __future__ import annotations

from typing import Any, Dict, List


def _convert_bbox_to_xywh(bbox: List[float]) -> List[float]:
    """
    若 bbox 疑似 [x_min, y_min, x_max, y_max]（即 x+width 或 y+height 超出 1.01），
    转为 [x, y, width, height]。否则原样返回。
    """
    if not isinstance(bbox, list) or len(bbox) != 4:
        return bbox
    try:
        a, b, c, d = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
    except (TypeError, ValueError):
        return bbox
    if a > c or b > d:
        return bbox
    # 若按 [x,y,w,h] 解释会超出相对范围 1.01，则按 [x1,y1,x2,y2] 转成 [x,y,w,h]
    if (a + c > 1.01) or (b + d > 1.01):
        return [a, b, max(1e-6, c - a), max(1e-6, d - b)]
    return bbox


def _flatten_style_into(obj: Dict[str, Any]) -> None:
    """将 obj.style 的键合并到 obj 顶层并删除 style。常见映射：background->background_color，font_size/color 保留。"""
    style = obj.pop("style", None)
    if not isinstance(style, dict):
        return
    for k, v in style.items():
        if k in obj:
            continue
        if k == "background":
            obj["background_color"] = v
        elif k == "font_size" and isinstance(v, (int, float)):
            # 绝对像素转相对比例近似：假设 16px ~ 0.02，20 ~ 0.025
            if v > 1:
                obj["font_size"] = min(0.08, v / 720.0)
            else:
                obj["font_size"] = v
        else:
            obj[k] = v


def _normalize_text_runs(runs: List[Any]) -> List[Dict[str, Any]]:
    """规范化 text_runs，并统一字段名：color->font_color, bold->font_weight, alignment->align（兼容 page_elements 等输出）。"""
    out: List[Dict[str, Any]] = []
    for r in runs:
        if isinstance(r, dict):
            _flatten_style_into(r)
            if r.get("text") is None and "text" not in r:
                r["text"] = ""
            if "color" in r and "font_color" not in r:
                r["font_color"] = r["color"]
            if "bold" in r and "font_weight" not in r:
                r["font_weight"] = "bold" if r.get("bold") in (True, "bold") else "normal"
            if "alignment" in r and "align" not in r:
                r["align"] = r["alignment"]
            out.append(r)
        else:
            out.append({"text": str(r)} if r is not None else {"text": ""})
    return out


def _normalize_element(elem: Dict[str, Any]) -> None:
    """原地规范化单个元素：bbox、style、text_runs、children；list_item 改为 text_box。"""
    if not isinstance(elem, dict):
        return

    if elem.get("type") == "list_item":
        elem["type"] = "text_box"

    bbox = elem.get("bbox")
    if isinstance(bbox, list):
        elem["bbox"] = _convert_bbox_to_xywh(bbox)

    _flatten_style_into(elem)

    for key in ("text_runs", "text_run"):
        runs = elem.get(key)
        if isinstance(runs, list):
            elem[key] = _normalize_text_runs(runs)
        elif isinstance(runs, dict):
            elem[key] = _normalize_text_runs([runs])

    if "icon" in elem and isinstance(elem["icon"], dict):
        ib = elem["icon"].get("bbox")
        if isinstance(ib, list):
            elem["icon"]["bbox"] = _convert_bbox_to_xywh(ib)

    children = elem.get("children")
    if isinstance(children, list):
        for ch in children:
            _normalize_element(ch)


def _convert_absolute_to_relative(
    elem: Dict[str, Any],
    parent_abs_bbox: List[float],
) -> None:
    """
    递归遍历：将 GLM 输出的全局绝对坐标 [x,y,w,h]，换算为相对父容器的 [x,y,w,h]。
    parent_abs_bbox 格式为 [p_x, p_y, p_w, p_h]（父容器在整页中的绝对 bbox）。
    """
    if not isinstance(elem, dict):
        return

    bbox = elem.get("bbox")
    if isinstance(bbox, list) and len(bbox) == 4 and len(parent_abs_bbox) == 4:
        try:
            p_x, p_y, p_w, p_h = (
                float(parent_abs_bbox[0]),
                float(parent_abs_bbox[1]),
                float(parent_abs_bbox[2]),
                float(parent_abs_bbox[3]),
            )
            c_x, c_y, c_w, c_h = (
                float(bbox[0]),
                float(bbox[1]),
                float(bbox[2]),
                float(bbox[3]),
            )
        except (TypeError, ValueError):
            current_abs_bbox = parent_abs_bbox
        else:
            if p_w > 0 and p_h > 0:
                rel_x = max(0.0, (c_x - p_x) / p_w)
                rel_y = max(0.0, (c_y - p_y) / p_h)
                rel_w = min(1.0, c_w / p_w)
                rel_h = min(1.0, c_h / p_h)
                elem["bbox"] = [rel_x, rel_y, rel_w, rel_h]
            current_abs_bbox = [c_x, c_y, c_w, c_h]
    else:
        current_abs_bbox = parent_abs_bbox

    children = elem.get("children")
    if isinstance(children, list):
        for ch in children:
            _convert_absolute_to_relative(ch, current_abs_bbox)


def normalize_glm_v2_output(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    对 GLM V2 原始 JSON 做清洗，使 bbox、样式、结构可被 create_slide_v2 使用。
    - 若有 page 无 slide_data：用 page 构造 slide_data。
    - 递归规范化：bbox [x1,y1,x2,y2]->[x,y,w,h]、扁平 style、list_item->text_box。
    - 最后将子元素的全局绝对坐标递归换算为相对父容器的坐标。
    """
    if not isinstance(raw, dict):
        return raw

    if "page" in raw and "slide_data" not in raw:
        page = raw["page"]
        if isinstance(page, dict):
            raw["slide_data"] = {
                "elements": page.get("elements", []),
                "background": page.get("background"),
            }

    elements = raw.get("slide_data", {}).get("elements") or raw.get("elements") or []
    if not isinstance(elements, list):
        return raw

    for el in elements:
        _normalize_element(el)

    for el in elements:
        bbox = el.get("bbox")
        if isinstance(bbox, list) and len(bbox) == 4:
            for child in el.get("children", []):
                _convert_absolute_to_relative(child, parent_abs_bbox=bbox)

    return raw
