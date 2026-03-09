"""连通性等测试接口。"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.pipeline.glm_layout_ocr import test_glm_connectivity
from app.pipeline.layout_ocr_models import LayoutOcrApiError

router = APIRouter(tags=["Test"])


@router.get("/test/glm")
async def test_glm():
    """
    测试智谱 GLM API 连通性：仅发一条极简文本请求，不传图。
    用于确认 GLM_API_KEY、网络与端点是否正常。
    """
    try:
        reply = test_glm_connectivity()
        return {"ok": True, "message": "连通正常", "reply": reply}
    except LayoutOcrApiError as e:
        return JSONResponse(
            status_code=503,
            content={"ok": False, "message": str(e)},
        )
