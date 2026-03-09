# NBLM2PPTX 验收标准 / UAT

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**相关文档**：[PRD](PRD.md)、[E2E_Verification.md](E2E_Verification.md)、[项目概述](project-overview.md)

---

## 1. 验收条款（可验证）

以下每条均可通过操作或检查判定通过/不通过。

| # | 条款 | 验证方式 |
|---|------|----------|
| A1 | 用户可上传 PDF（≤MAX_FILE_SIZE、允许扩展名），并得到 task_id | 调用 POST /upload，响应含 task_id |
| A2 | 用户可查询任务状态（pending/running/completed/failed）与进度 | GET /tasks/{task_id} 返回 status、progress 等 |
| A3 | 任务进行中或完成后，用户可通过 WebSocket 或轮询获得进度更新 | 连接 /ws/progress 或轮询 GET /tasks/{id}，progress 随任务推进变化 |
| A4 | 任务完成后用户可下载生成的 PPTX 文件 | GET /export/{task_id} 返回 200 及 .pptx 流 |
| A5 | 单页失败时任务仍可完成，导出结果包含成功页与降级页；用户可区分失败页 | 使用会触发单页失败的素材验证；导出 PPTX 可打开，失败页为降级占位 |
| A6 | 前端可完成：上传 → 选页（可选）→ 查看进度 → 导出 PPTX | 按 [E2E_Verification.md](E2E_Verification.md) 执行正向流程 |
| A7 | 无效或缺失 GEMINI_API_KEY 时，后端/流水线报错，用户可见明确提示 | 不设或错误 Key，上传后任务失败，前端有错误态 |
| A8 | 文档与部署就绪：README、Deployment、E2E 验证文档、API/Schema 存在且可循 | 人工检查文档与部署步骤可执行 |

## 2. 与 PRD 的对应

- PRD §7 质量与验收（文字覆盖率、位置/样式、稳定性）针对「纯前端/NotebookLM」形态；本仓库为全栈实现，以上 A1–A8 覆盖当前交付范围。
- 若需补充 PRD 中的具体质量指标（如单页耗时、成功率），可在后续迭代中增加可测条款。

## 3. 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿，与 E2E 及 Memory ROOT 对齐 |
