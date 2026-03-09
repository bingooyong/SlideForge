# NBLM2PPTX 系统架构设计

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**相关文档**：[项目概述](project-overview.md)、[技术选型](tech-stack.md)、[详细设计](Design.md)、[部署手册](Deployment.md)

---

## 1. 概述与设计目标

- 与 [项目概述](project-overview.md) 一致：将 PDF/图片解析为版面、文字、样式、图标与配色，经背景净化与结构化重组，生成可编辑 PPTX。
- 设计目标：前后端分离、流水线可测可替换、单页失败可降级、进度可观测（WebSocket）、文档与部署就绪。

## 2. 系统边界与上下文

- **用户**：通过浏览器上传 PDF/图片，选择页面与选项，查看进度，下载 PPTX。
- **外部依赖**：Google Gemini API（版面/OCR）；无其他必须的外部服务。
- **边界**：后端负责上传存储、流水线执行、任务状态、导出文件；前端负责 UI、轮询或 WebSocket 进度、触发导出。

## 3. 组件/服务列表与职责

| 组件 | 职责 | 位置 |
|------|------|------|
| API v1 | 上传（POST /upload）、任务查询（GET /tasks/{id}）、导出（GET /export/{id}）、WebSocket（/ws/progress） | backend/app/api/v1/ |
| PipelineService | 编排单页流水线：PDF→页图→Gemini 版面/OCR→配色→图标裁剪→背景净化→PPTX 单页合成；汇总为整份 PPTX；推送进度 | backend/app/pipeline/pipeline_service.py |
| pdf_to_images | PDF→PageImage 列表（PyMuPDF） | backend/app/pipeline/pdf_to_images.py |
| gemini_layout_ocr | 单页图像→Slide（版面+TextBlock/ImageBlock+可选样式） | backend/app/pipeline/gemini_layout_ocr.py |
| color_extraction | 从页图提取 StyleInfo（主题色等） | backend/app/pipeline/color_extraction.py |
| icon_cropping | 按 ImageBlock 裁剪图标 | backend/app/pipeline/icon_cropping.py |
| background_cleaning | 背景净化（去字/弱化文字） | backend/app/pipeline/background_cleaning.py |
| pptx_composition | 单页/整份 PPTX 合成（python-pptx）；支持 add_slide_degraded 降级页 | backend/app/pipeline/pptx_composition.py |
| InMemoryTaskStore | 任务状态与进度存储（内存） | backend/app/core/task_store.py |
| 前端应用 | 上传、选页、进度展示、导出；可轮询或 WebSocket | frontend/src/ |

## 4. 数据流与关键交互

1. **上传**：前端 POST /upload → 后端落盘 UPLOAD_DIR/tasks/{task_id}/，创建任务并启动后台 PipelineService。
2. **进度**：PipelineService 更新 TaskStatus；前端通过 GET /tasks/{id} 或 WebSocket /ws/progress 获取进度。
3. **流水线（单页）**：PageImage → Gemini Slide → StyleInfo → 图标裁剪 → 背景净化 → create_slide；任一步失败可走 add_slide_degraded 降级页。
4. **导出**：GET /export/{task_id} 返回已生成的 PPTX 文件流。

## 5. 部署与运行环境拓扑

- **本地开发**：后端 uvicorn（默认 8000）；前端 Vite dev（默认 5173），代理 /api 到后端。
- **生产**：后端 uvicorn 或多 worker；前端 build 后静态资源由 Nginx/同域提供；可选 Docker Compose 一键后端。
- 无数据库；任务与上传文件均在单机（UPLOAD_DIR、内存任务表）。

## 6. 技术栈与关键依赖

- 见 [技术选型](tech-stack.md)。关键：FastAPI、Gemini、OpenCV、python-pptx、React、WebSocket、structlog。

## 7. 非功能考量

- **可用性**：单页失败不阻塞整批；降级策略见 [degradation-strategy.md](degradation-strategy.md)。
- **可扩展性**：PipelineService 可配置并发页数（PIPELINE_MAX_WORKERS）；任务存储可替换为 Redis/DB。
- **安全**：GEMINI_API_KEY 仅后端使用；上传类型与大小限制；CORS 可配置；见 [安全设计](security.md)。

---

## 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿，与 Memory ROOT 及代码结构一致 |
