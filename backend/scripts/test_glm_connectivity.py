#!/usr/bin/env python3
"""
测试智谱 GLM API 连通性：用简单对话检查端点与模型是否可用（不发图）。

用法（在 backend 目录下）:
  python scripts/test_glm_connectivity.py
  python scripts/test_glm_connectivity.py --model glm-4v-plus   # 仅测指定模型

会依次测试：1) 端点 + 文本模型（glm-4-flash） 2) 版面用视觉模型（GLM_LAYOUT_MODEL），
便于确认 Coding 端点与各模型是否可用。若视觉模型返回 429「余额不足或无可用资源包」，
表示该模型在 Coding 端点不占套餐额度，需用通用端点 + 账户余额或单独资源包。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.pipeline.glm_layout_ocr import _test_glm_simple_chat
from app.pipeline.layout_ocr_models import LayoutOcrApiError


def main() -> int:
    base = getattr(settings, "GLM_API_BASE", None) or "https://open.bigmodel.cn/api/paas/v4"
    base = base.rstrip("/")
    print(f"端点: {base}", flush=True)
    print(f"API Key: {'已配置' if settings.GLM_API_KEY else '未配置'}", flush=True)
    if not settings.GLM_API_KEY:
        print("请设置 .env 中的 GLM_API_KEY", file=sys.stderr)
        return 1

    models_to_test = []
    if len(sys.argv) > 1 and sys.argv[1] == "--model" and len(sys.argv) > 2:
        models_to_test = [sys.argv[2]]
    else:
        models_to_test = [
            "glm-4-flash",
            getattr(settings, "GLM_LAYOUT_MODEL", "glm-4v-plus") or "glm-4v-plus",
        ]
        if models_to_test[0] == models_to_test[1]:
            models_to_test = [models_to_test[0]]

    for i, model in enumerate(models_to_test, 1):
        print(f"\n[{i}/{len(models_to_test)}] 测试模型: {model} ...", flush=True)
        try:
            reply = _test_glm_simple_chat(
                model=model,
                user_content="请只回复：OK",
                timeout_connect=10.0,
                timeout_read=20.0,
            )
            print(f"  结果: 可用，回复: {reply[:80]!r}", flush=True)
        except LayoutOcrApiError as e:
            print(f"  结果: 失败 - {e}", file=sys.stderr)
            return 1

    print("\n全部模型可用，API 与端点正常。", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
