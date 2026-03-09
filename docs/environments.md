# NBLM2PPTX 环境说明

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**相关文档**：[部署手册](Deployment.md)、[配置说明](configuration.md)

---

## 1. 环境列表与用途

| 环境 | 用途 | 后端地址 | 前端地址 | 说明 |
|------|------|----------|----------|------|
| 本地开发 | 开发、调试、E2E 验证 | http://127.0.0.1:8000 | http://localhost:5173 | 后端 --reload；前端 Vite 代理 /api |
| 生产 / 自建 | 演示或内网部署 | 由部署决定（如 :8000 + Nginx） | 同域或静态托管 | 无 --reload；CORS_ORIGINS 按需设置 |

当前项目不区分「测试/预发」环境；若有需要可在此补充。

## 2. 环境差异要点

- **本地开发**：Python 3.11+、Node 18+；依赖见 [Deployment.md](Deployment.md)；`.env` 仅本地使用，不提交。
- **生产**：需设置 GEMINI_API_KEY、UPLOAD_DIR、LOG_LEVEL 等；前端 build 后由静态服务或与后端同域提供；HTTPS 建议由反向代理完成。

## 3. 相关文档

- 具体启动步骤与 Docker 见 [Deployment.md](Deployment.md)。
- 配置项说明见 [configuration.md](configuration.md)。

---

## 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿 |
