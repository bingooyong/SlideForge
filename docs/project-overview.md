# NBLM2PPTX 项目概述 / 项目章程

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**与 Memory ROOT 对应**：见 [.apm/Memory/Memory_Root.md](../.apm/Memory/Memory_Root.md)

---

## 1. 项目目标

- **一句话目标**：将 PDF/图片按页解析出版面、文字、样式、图标与配色，通过背景净化与结构化重组，生成可编辑的 PPTX 幻灯片（本地简化版 Codia.ai 形态）。
- 与 Memory ROOT 一致：技术栈为 Python FastAPI 后端 + React+Vite+Zustand 前端；先确定 Schema 与 API 契约，再实现流水线（Gemini 版面/OCR、OpenCV 配色、python-pptx 合成）与 WebSocket 实时进度；目标是高质量、可落地的图片转可编辑 PPTX 解决方案。

## 2. 范围与边界

**在范围内：**

- 上传 PDF 或图片，按页解析版面、文字、样式、图标与主题色。
- 流水线：PDF→页图、Gemini 版面/OCR、OpenCV 主题色与图标裁剪、背景净化、python-pptx 单页合成；WebSocket 实时进度。
- 前端：上传与选页 UI、任务状态与进度展示、导出 PPTX。
- 单页失败时按页降级；文档与部署就绪（README、Deployment、E2E 验证、Docker 可选）。

**不在范围内：**

- 用户账号与权限、多租户存储。
- 自动品牌模板、动画生成、合规审核（仅依赖 Gemini 版权提示）。
- 离线或纯前端单页形态（本仓库为全栈实现）。

## 3. 成功准则

- 真实 PDF 上传后可生成可编辑 PPTX；单页失败不阻塞整批，按页降级可查。
- 端到端流程可验证：上传→进度→导出，见 [E2E_Verification.md](E2E_Verification.md)。
- 文档与部署就绪：README、[Deployment.md](Deployment.md)、[PRD](PRD.md)、API/Schema、降级策略齐全；可选 Docker 一键运行。
- Phase 01–04 全部完成，项目发布就绪（与 Memory ROOT 一致）。

## 4. 约束与假设

- **技术约束**：后端 FastAPI、前端 React；依赖 Gemini API（版面/OCR）、OpenCV、python-pptx；需配置 GEMINI_API_KEY。
- **资源假设**：单机部署；上传与任务文件落盘于 UPLOAD_DIR；无持久化数据库，任务状态内存存储（InMemoryTaskStore）。
- **合规**：用户需自备 Gemini API Key；素材版权由用户负责，Gemini 返回版权相关错误时直接失败提示。

## 5. 相关文档

- [文档索引](INDEX.md)
- [PRD](PRD.md)、[PRD-zh](PRD-zh.md)
- [详细设计](Design.md)
- [部署手册](Deployment.md)
- [术语表](glossary.md)

## 6. 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿，与 Memory ROOT 及全栈实现对齐 |
