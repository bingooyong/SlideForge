# NBLM2PPTX 新成员上手（Onboarding）

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**相关文档**：[文档索引](INDEX.md)、[环境说明](environments.md)、[配置说明](configuration.md)、[部署手册](Deployment.md)

---

## 1. 项目是什么

NBLM2PPTX：将 PDF/图片转为可编辑 PPTX 的全栈应用（FastAPI 后端 + React 前端）。详见 [项目概述](project-overview.md) 与仓库 [README](../README.md)。

## 2. 环境搭建

- **后端**：Python 3.11+，进入 `backend/`，`pip install -r requirements.txt`，`cp .env.example .env`，在 `.env` 中填入 `GEMINI_API_KEY`。
- **前端**：Node.js 18+，进入 `frontend/`，`npm install`。
- 启动：后端 `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`；前端 `npm run dev`。详见 [Deployment.md](Deployment.md)。

## 3. 首次运行与验证

- 浏览器打开 http://localhost:5173，上传一份 PDF，等待进度完成，点击导出 PPTX。若遇问题见 [E2E_Verification.md](E2E_Verification.md)。
- API 文档：http://127.0.0.1:8000/docs。

## 4. 文档与规范

- **文档地图**：[docs/INDEX.md](INDEX.md)。
- **代码规范**：[Code_Standards.md](Code_Standards.md)、[standards/](standards/)。
- **架构与设计**：[architecture.md](architecture.md)、[Design.md](Design.md)、[tech-stack.md](tech-stack.md)。

## 5. 权限与仓库

- 按团队约定申请代码仓库权限、Gemini API Key（或使用团队共享测试 Key）；不提交 `.env`。

---

## 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿 |
