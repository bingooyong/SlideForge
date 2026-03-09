# NBLM2PPTX 运维手册

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**相关文档**：[部署手册](Deployment.md)、[架构设计](architecture.md)、[配置说明](configuration.md)

---

## 1. 服务/组件清单

| 组件 | 职责 | 启停方式 |
|------|------|----------|
| 后端 | FastAPI：上传、任务、导出、WebSocket | uvicorn app.main:app --host 0.0.0.0 --port 8000 |
| 前端 | 静态资源（生产为 build 后 dist/） | 静态服务器或 Nginx 托管 |
| 流水线 | 后端进程内执行，无独立进程 | 随后端启停 |

无数据库、无独立消息队列；任务状态在内存中，重启后丢失。

## 2. 日常操作

- **启停**：按 [Deployment.md](Deployment.md) 启动后端与前端；停止即结束进程（或 `docker compose down`）。
- **扩缩容**：单机部署时调整 `WORKERS`、`PIPELINE_MAX_WORKERS`；多实例需后续引入共享任务存储（当前未实现）。
- **备份**：重要时备份 `UPLOAD_DIR`（上传与生成文件）；日志在 `backend/logs/`（若已配置）。
- **日志**：structlog 输出；`LOG_LEVEL` 控制级别；日志轮转需自行配置（如 logrotate）。

## 3. 配置变更

- 修改 `backend/.env` 后需重启后端生效。
- 不提交 `.env`；生产配置通过环境变量或密钥管理注入。

## 4. 监控与告警

- 当前无内置监控；可对 `/health` 做健康检查。
- 告警与 Runbook 见 [monitoring.md](monitoring.md)（待补充）、[runbooks/](runbooks/)（待补充）。

## 5. 故障与应急

- 单页失败：见 [degradation-strategy.md](degradation-strategy.md)；用户可见失败页与导出结果。
- 服务不可用：检查 GEMINI_API_KEY、磁盘空间、进程与端口；日志见 backend 输出或 logs/。

---

## 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿 |
