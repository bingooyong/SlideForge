# NBLM2PPTX 常见问题（FAQ）

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  

---

## 使用与功能

**Q：支持哪些上传格式？**  
A：PDF 及图片（jpg、jpeg、png、webp、bmp），具体以配置 `ALLOWED_EXTENSIONS` 为准；单文件大小受 `MAX_FILE_SIZE` 限制（默认 50MB）。

**Q：任务失败或某一页失败怎么办？**  
A：单页失败会按「按页降级」处理，导出结果中该页为降级占位；整任务失败时请查看后端日志或前端错误提示。常见原因：GEMINI_API_KEY 无效、配额超限、PDF 损坏或加密。详见 [degradation-strategy.md](degradation-strategy.md)。

**Q：如何获取 Gemini API Key？**  
A：在 [Google AI Studio](https://aistudio.google.com/apikey) 申请；在后端 `backend/.env` 中设置 `GEMINI_API_KEY`。

**Q：进度不更新？**  
A：确认后端正常、任务未失败；前端可通过轮询 GET /tasks/{task_id} 或 WebSocket /ws/progress 获取进度。检查网络与 CORS 配置。

---

## 开发与部署

**Q：本地如何同时跑前端和后端？**  
A：两个终端：一在后端目录执行 `uvicorn app.main:app --reload ...`，一在前端目录执行 `npm run dev`。前端会将 /api 代理到后端。见 [Deployment.md](Deployment.md)。

**Q：生产环境如何部署？**  
A：后端用 uvicorn 多 worker 或 Docker；前端 `npm run build` 后托管 dist/；配置 GEMINI_API_KEY、UPLOAD_DIR、CORS 等。见 [Deployment.md](Deployment.md)、[configuration.md](configuration.md)。

**Q：有没有 Docker 一键运行？**  
A：有。项目根目录可配合 `docker-compose.yml` 启动后端；前端需在宿主机或另行构建。见 README「Docker 启动」与 [Deployment.md](Deployment.md)。

---

## 文档与规范

**Q：文档在哪里找？**  
A：入口为 [docs/INDEX.md](INDEX.md)（文档索引）；README 中有「文档与规范」链接。

---

## 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿 |
