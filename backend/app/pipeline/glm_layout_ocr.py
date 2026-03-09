"""
智谱 GLM 版面 OCR：仅负责调用智谱开放平台视觉模型，返回原始文本。

职责：速率限制 + HTTP 调用 GLM API；V2 时提供专用提示词（无 response_schema，用硬模板约束）。
"""

from __future__ import annotations

import time
from collections import deque
from threading import Lock
from typing import Optional

import httpx

from app.config import settings
from app.pipeline.layout_ocr_models import (
    LayoutOcrApiError,
    LayoutOcrInvalidResponseError,
    parse_retry_seconds_429,
)

_GLM_RATE_LOCK = Lock()
_GLM_CALL_TIMESTAMPS: deque[float] = deque()


def test_glm_connectivity(model: str | None = None) -> str:
    """
    仅测试智谱 API 连通性：发一条极简文本请求，不传图。

    Args:
        model: 模型名，不传则用 glm-4-flash（文本模型，兼容性最好）。

    Returns:
        模型简短回复内容，表示连通正常。

    Raises:
        LayoutOcrApiError: 未配置 Key、网络超时或 API 返回错误。
    """
    return _test_glm_simple_chat(
        model=model or "glm-4-flash",
        user_content="请只回复：连通正常",
    )


def _test_glm_simple_chat(
    model: str,
    user_content: str = "你好，请回复OK",
    timeout_connect: float = 10.0,
    timeout_read: float = 20.0,
) -> str:
    """
    向当前配置的 GLM 端点发一条纯文本对话，用于测试端点与指定模型是否可用。
    不传图、不经过速率限制。
    """
    if not settings.GLM_API_KEY:
        raise LayoutOcrApiError("GLM_API_KEY 未配置，请在 .env 中设置。")
    base_url = (settings.GLM_API_BASE or "https://open.bigmodel.cn/api/paas/v4").rstrip("/")
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": user_content}],
        "max_tokens": 64,
    }
    timeout = httpx.Timeout(timeout_connect, read=timeout_read)
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                url,
                headers={
                    "Authorization": f"Bearer {settings.GLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.TimeoutException as exc:
        raise LayoutOcrApiError(
            f"智谱 API 超时（{model}）: {exc}. 请检查网络或端点是否可达。"
        ) from exc
    except Exception as exc:
        raise LayoutOcrApiError(f"智谱 API 连接异常: {exc}") from exc

    if resp.status_code >= 400:
        try:
            body = resp.json()
            err = body.get("error") if isinstance(body.get("error"), dict) else None
            msg = (err.get("message") if err else None) or resp.text[:300]
        except Exception:
            msg = resp.text[:300]
        raise LayoutOcrApiError(
            f"智谱 API（{model}）返回 HTTP {resp.status_code}: {msg}. "
            "请检查 API Key、模型名及端点（Coding 套餐需用 api/coding/paas/v4）。"
        )

    data = resp.json()
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    return content.strip() or "ok"


def build_prompt_v2_glm() -> str:
    """
    GLM 专用 V2 提示词：与 Gemini 一致，根节点直接使用 background + elements，不要 slide_data 包装。
    坐标可为相对父容器或全局比例；后端 Normalizer 会做兼容转换。
    """
    return """
你是一个顶级的 UI/UX 前端工程师和 PPTX 版式分析专家。你需要对上传的幻灯片图片进行深度的「逆向工程」，将其拆解为结构化 JSON 数据，以便 1:1 还原为可编辑的 PPTX。

【核心法则 1：极限 OCR】提取的文本必须 100% 字对字忠实于原图，禁止润色、扩写或省略。

【核心法则 2：坐标与嵌套】bbox 格式为 [x, y, width, height]，数值 0.0~1.0。卡片/线框内的内容必须用 "type": "group" 包裹，子元素放在 children 数组中；子元素 bbox 建议相对父容器，也可用全局比例（后端会兼容）。

【核心法则 3：字号】font_size 必须为相对幻灯片高度的比例小数（如 0.028、0.045），禁止输出 16、20 等像素值。

【核心法则 4：根结构 - 重要】不要使用 slide_data 包装！根节点直接包含 "background" 和 "elements"（与 Gemini 一致）。可选 "page_id"。

节点类型：纯文本用 "text_box"；带背景色/边框用 "shape_text_box"；带前置图标用 "icon_text_layout"；列表用 "list_layout" 或 "list_block"。富文本用 text_runs 数组，每项含 text、font_size、color（或 font_color）、font_weight、align。形状用 fill_color 或 background_color、border_radius 或 radius。

直接输出纯 JSON，不要带 Markdown 代码块。格式范例（根为 background + elements，无 slide_data）：

{"background":{"type":"gradient","start_color":"#E6F0F6","end_color":"#F8FBFD"},"elements":[{"type":"group","bbox":[0.05,0.18,0.43,0.75],"background_color":"#FFFFFF","border_radius":0.015,"children":[{"type":"shape_text_box","bbox":[0.04,0.04,0.92,0.08],"fill_color":"#3471A1","border_radius":0.008,"text_runs":[{"text":"【能力域：设立安全门限要求】","font_size":0.045,"color":"#FFFFFF","font_weight":"bold","align":"center"}]},{"type":"icon_text_layout","bbox":[0.04,0.15,0.92,0.10],"placeholder_id":"icon_check","text_runs":[{"text":"全面覆盖 (通过) : ","font_size":0.028,"color":"#000000","font_weight":"bold"},{"text":"已建立针对CA产品...","font_size":0.028,"color":"#000000","font_weight":"normal"}]}]}]}
"""


def _respect_glm_rate_limit() -> None:
    max_rpm = getattr(settings, "GLM_MAX_RPM", 60)
    if max_rpm <= 0:
        return
    while True:
        now = time.time()
        with _GLM_RATE_LOCK:
            cutoff = now - 60.0
            while _GLM_CALL_TIMESTAMPS and _GLM_CALL_TIMESTAMPS[0] < cutoff:
                _GLM_CALL_TIMESTAMPS.popleft()
            if len(_GLM_CALL_TIMESTAMPS) < max_rpm:
                _GLM_CALL_TIMESTAMPS.append(now)
                return
            sleep_for = _GLM_CALL_TIMESTAMPS[0] + 60.0 - now
        if sleep_for > 0:
            time.sleep(sleep_for)
        else:
            time.sleep(60.0 / max_rpm)


def call_glm_raw(
    prompt: str,
    image_b64: str,
    max_retries: int = 5,
    base_delay: float = 1.0,
) -> str:
    """
    调用智谱 GLM 视觉模型（open.bigmodel.cn），返回模型输出的文本。

    Raises:
        LayoutOcrApiError: API 调用失败。
        LayoutOcrInvalidResponseError: 返回 content 为空。
    """
    if not settings.GLM_API_KEY:
        raise LayoutOcrApiError(
            "GLM_API_KEY is not configured (LAYOUT_OCR_PROVIDER=glm 时必填)."
        )
    base_url = (settings.GLM_API_BASE or "https://open.bigmodel.cn/api/paas/v4").rstrip("/")
    url = f"{base_url}/chat/completions"
    model = getattr(settings, "GLM_LAYOUT_MODEL", "glm-4v-plus")
    image_data_url = f"data:image/png;base64,{image_b64}"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        "temperature": 0.2,
        "max_tokens": 8192,
    }

    def _glm_error_message(resp: httpx.Response) -> str:
        try:
            body = resp.json()
            err = body.get("error") if isinstance(body.get("error"), dict) else None
            msg = err.get("message") if err else None
            code = err.get("code") if err else None
            if msg or code:
                return f"HTTP {resp.status_code} error={code} message={msg}" if code else f"HTTP {resp.status_code} {msg}"
        except Exception:
            pass
        return f"HTTP {resp.status_code} body={resp.text[:500]!r}"

    last_error: Optional[Exception] = None
    last_status: Optional[int] = None
    last_body: Optional[str] = None
    # 连接超时 15s、读取超时 90s，避免无响应时长时间挂起
    timeout = httpx.Timeout(15.0, read=90.0)
    for attempt in range(max_retries):
        try:
            _respect_glm_rate_limit()
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {settings.GLM_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
            if resp.status_code == 429:
                last_error = RuntimeError(f"HTTP 429 限流: {resp.text[:200]!r}")
                last_status = 429
                last_body = resp.text
                wait = parse_retry_seconds_429(Exception(resp.text)) or 60.0
                if attempt == max_retries - 1:
                    raise LayoutOcrApiError(
                        f"GLM API 限流（429）已达 {max_retries} 次重试. 请稍后重试或调低 GLM_MAX_RPM。"
                    )
                time.sleep(wait)
                continue
            if resp.status_code >= 400:
                last_status = resp.status_code
                last_body = resp.text
                err_msg = _glm_error_message(resp)
                if attempt == max_retries - 1:
                    raise LayoutOcrApiError(
                        f"GLM API 请求失败: {err_msg}. "
                        "请检查 API Key、模型名及端点 https://docs.bigmodel.cn/cn/api/introduction"
                    )
                last_error = RuntimeError(err_msg)
                time.sleep(base_delay * (2**attempt))
                continue
            data = resp.json()
            content = (data.get("choices") or [{}])[0].get("message", {}).get("content")
            if not content:
                raise LayoutOcrInvalidResponseError(
                    "GLM 返回的 choices[0].message.content 为空."
                )
            return content
        except (LayoutOcrApiError, LayoutOcrInvalidResponseError):
            raise
        except httpx.TimeoutException as exc:
            last_error = exc
            if attempt == max_retries - 1:
                raise LayoutOcrApiError(
                    f"GLM API 请求超时: {exc}. 请检查网络或代理，或稍后重试。"
                ) from exc
            time.sleep(base_delay * (2**attempt))
        except httpx.HTTPStatusError as exc:
            last_error = exc
            last_status = getattr(exc.response, "status_code", None)
            last_body = getattr(exc.response, "text", None) if exc.response else None
            if attempt == max_retries - 1:
                detail = _glm_error_message(exc.response) if exc.response else f"{exc}"
                raise LayoutOcrApiError(
                    f"GLM API 请求失败: {detail}. "
                    "请检查 API Key、模型名及端点 https://docs.bigmodel.cn/cn/api/introduction"
                ) from exc
            time.sleep(base_delay * (2**attempt))
        except Exception as exc:
            last_error = exc
            if attempt == max_retries - 1:
                err_str = str(exc).strip() if (exc and str(exc)) else f"{type(exc).__name__}: {exc!r}"
                raise LayoutOcrApiError(
                    f"GLM API 调用失败（共 {max_retries} 次）: {err_str}. "
                    "请检查网络、API Key 与端点 https://docs.bigmodel.cn/cn/api/introduction"
                ) from exc
            time.sleep(base_delay * (2**attempt))
    if last_error is not None and str(last_error):
        err_str = str(last_error)
    elif last_status is not None:
        err_str = f"HTTP {last_status} body={(last_body or '')[:300]!r}"
    else:
        err_str = (
            f"{type(last_error).__name__}: {last_error!r}"
            if last_error is not None
            else "未知错误（请检查网络或 API 响应）"
        )
    raise LayoutOcrApiError(f"GLM API 调用失败: {err_str}")  # pragma: no cover
