# NBLM2PPTX 配置说明

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**相关文档**：[环境说明](environments.md)、[部署手册](Deployment.md)；配置来源：`backend/.env.example`、`backend/app/config.py`

---

## 1. 后端配置（backend/.env）

以下为 `backend/.env.example` 中的配置项说明；复制为 `backend/.env` 后按需修改，**不要提交 .env**。

### 1.1 必填

| 变量 | 说明 | 示例 |
|------|------|------|
| GEMINI_API_KEY | Gemini API Key，用于版面/OCR | 从 [Google AI Studio](https://aistudio.google.com/apikey) 获取 |

### 1.2 上传与存储

| 变量 | 说明 | 默认值 |
|------|------|--------|
| UPLOAD_DIR | 上传与任务文件根目录（其下创建 tasks/{task_id}/） | ./uploads |
| MAX_FILE_SIZE | 单文件最大字节数 | 52428800（50MB） |
| ALLOWED_EXTENSIONS | 允许的扩展名，逗号分隔小写 | pdf,jpg,jpeg,png,webp,bmp |

### 1.3 Gemini（可选）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| GEMINI_LAYOUT_MODEL | 版面分析模型 | gemini-1.5-pro |
| GEMINI_MAX_RPM | 每分钟请求上限 | 15 |

### 1.4 服务（可选）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| CORS_ORIGINS | CORS 允许源（* 表示任意） | * |
| LOG_LEVEL | 日志级别 | INFO |
| WORKERS | Uvicorn 工作进程数 | 2 |
| TASK_TIMEOUT | 单任务超时秒数 | 3600 |
| PIPELINE_MAX_WORKERS | 每任务最大并发处理页数 | 3 |

## 2. 前端

- 开发时通过 Vite 代理将 `/api` 转发到后端（默认 http://127.0.0.1:8000），见 `frontend/vite.config.ts`。
- 生产构建后，API 基础 URL 由代理或同域决定，通常无需单独配置。

## 3. 安全注意

- 不要将 `GEMINI_API_KEY` 或 `.env` 提交到仓库。
- 生产环境建议设置明确的 `CORS_ORIGINS`，避免 `*`。

---

## 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿，与 backend/.env.example 一致 |
