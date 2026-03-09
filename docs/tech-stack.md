# NBLM2PPTX 技术选型说明

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**相关文档**：[项目概述](project-overview.md)、[架构设计](architecture.md)

---

## 1. 选型总览

| 类别 | 选定方案 | 主要用途 |
|------|----------|----------|
| 后端框架 | FastAPI | REST API、WebSocket、后台任务、OpenAPI 文档 |
| 前端框架 | React + Vite + TypeScript | 上传/选页 UI、进度展示、状态管理 |
| 状态管理 | Zustand | 前端任务状态与 UI 状态 |
| PDF 解析 | PyMuPDF (fitz) | PDF→页图（后端） |
| 版面/OCR | Google Gemini API | 版面分析、文字与坐标（及样式） |
| 图像处理 | OpenCV | 主题色提取、图标裁剪、背景净化相关 |
| PPTX 生成 | python-pptx | 单页与整份 PPTX 合成 |
| 实时进度 | WebSocket | 任务进度推送 |
| 任务存储 | InMemoryTaskStore（内存） | 任务状态与生命周期，可替换为持久化 |
| 日志 | structlog | 结构化日志与错误追踪 |

## 2. 选型理由与权衡

- **FastAPI**：异步支持、自动 OpenAPI、与 Python 生态（PyMuPDF、OpenCV、python-pptx）集成简单；替代方案如 Flask 需自行补 WebSocket 与异步。
- **React + Vite**：与现有前端规范一致，Vite 开发体验与构建速度好；Zustand 轻量，满足任务状态与进度展示。
- **Gemini**：满足版面理解与 OCR 质量要求，需 API Key 与配额管理；替代方案可为其他多模态/OCR 服务，需改 pipeline 适配。
- **python-pptx**：服务端生成 PPTX 的成熟方案，可编程控制版式与样式；替代方案可为服务端调用 Office 等，复杂度更高。
- **InMemoryTaskStore**：首版简化实现，无数据库依赖；后续可改为 Redis 或 DB 以支持重启恢复与多实例。

## 3. 版本与配置

- 后端依赖见 `backend/requirements.txt`；环境变量见 [configuration.md](configuration.md) 与 `backend/.env.example`。
- 前端依赖见 `frontend/package.json`。
- Gemini 模型与限流：默认 `GEMINI_LAYOUT_MODEL=gemini-1.5-pro`，`GEMINI_MAX_RPM=15`，可在 `.env` 中调整。

## 4. 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿，与 Memory ROOT 及现有实现一致 |
