# NBLM2PPTX 测试计划

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**相关文档**：[PRD](PRD.md)、[验收标准](acceptance.md)、[E2E_Verification.md](E2E_Verification.md)

---

## 1. 测试目标与范围

- **目标**：保障上传→任务→进度→导出端到端可用，单页降级与错误路径符合预期，文档与部署可复现。
- **范围**：后端 API 与流水线、前端上传与进度与导出、集成与 E2E；不含性能/压力正式基准。

## 2. 测试类型

| 类型 | 范围 | 说明 |
|------|------|------|
| 单元测试 | 后端 pipeline 各模块、task_store、工具函数 | 见 backend/tests/unit/；覆盖率见 Phase 3.10 |
| 集成测试 | API 路由、上传/任务/导出/WebSocket 桩 | 见 backend/tests/integration/ |
| E2E | 浏览器：上传 PDF → 进度 → 导出 PPTX；错误路径（无效 Key、损坏 PDF 等） | 按 [E2E_Verification.md](E2E_Verification.md) 执行 |

## 3. 环境与数据

- 本地开发环境：后端 + 前端本地启动；需有效 GEMINI_API_KEY（E2E 与真实流水线）。
- 测试用 PDF：见 E2E_Verification 与 PRD 验收素材建议（NotebookLM 输出、多页、中英混排等）。

## 4. 通过准则

- 单元/集成：CI 中 pytest 通过；无新增严重回归。
- E2E：验收条款 [acceptance.md](acceptance.md) A1–A8 可验证通过；文档步骤可执行。

## 5. 风险与假设

- 依赖 Gemini API 可用性与配额；失败/超时由降级与重试策略覆盖。
- 当前无自动化 E2E（如 Playwright）；E2E 以人工按文档验证为主，可后续补充自动化。

## 6. 基于 raw 文件的 PPTX 质量测试

当已有「版面 OCR 大模型原始输出」文件（如 `demo-001_llm_raw_gemini_gemini-2_5-flash_v2.txt`）时，可不调 API 直接生成 PPTX，用于离线对比与质量评估。

### 6.1 生成 PPTX

在 `backend` 目录下执行：

```bash
# 指定 raw 文件与对应原图
python scripts/run_pptx_from_raw.py ../assets/demo-001_llm_raw_gemini_gemini-2_5-flash_v2.txt --image ../assets/demo-001.jpg -o ../assets/demo-001_from_raw.pptx

# 不传 --image 时，会按 raw 文件名推断原图（如 demo-001_llm_raw_xxx.txt → demo-001.jpg）
python scripts/run_pptx_from_raw.py ../assets/demo-001_llm_raw_gemini_gemini-2_5-flash_v2.txt -o out.pptx
```

输出 PPTX 与正常流水线一致：背景净化 + 按 V2 Schema 渲染文字/容器/列表。

### 6.2 质量评估建议

- **目视对比**：用 PowerPoint/Keynote 打开生成的 PPTX，与原始截图或 PDF 页面对比，检查版式、层级、文字是否一致、有无漏字/错位。
- **文本核对**：从 raw 文件中提取关键文案，在 PPTX 中逐段确认是否完整、无乱码或样式错用。
- **回归对比**：同一张图用不同模型或不同 raw 输出生成多份 PPTX，对比版式与可编辑性，用于评估模型或提示词改动。

### 6.3 页面上传流水线的中间产物（与脚本对比调试）

页面上传 PDF 后，流水线会在任务目录下写入中间文件，便于与 `run_pptx_from_raw.py` 对比：

- **任务目录**：`{UPLOAD_DIR}/tasks/{task_id}/`（如 `uploads/tasks/bb225c33-.../`）。
- **每页输入图**：`page_{0-based}_input.png`，即 PDF 转图后送入大模型的那一页图像。
- **每页 LLM 原始输出**：`page_{0-based}_llm_raw_v2.txt`，即 V2 版面 OCR 的原始 JSON 文本。
- 日志中会打出 `pipeline_raw_v2_saved`，含 `path`，便于定位文件。

用命令行复现「页面导出」效果（同一输入、同一 JSON）：

```bash
cd backend
python scripts/run_pptx_from_raw.py "uploads/tasks/<task_id>/page_0_llm_raw_v2.txt" --image "uploads/tasks/<task_id>/page_0_input.png" -o compare.pptx
```

若 `compare.pptx` 与页面导出的 PPTX 一致，则差异来自输入图或 LLM 每次返回不同；若不一致，则重点排查解析/渲染路径。

---

## 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿 |
