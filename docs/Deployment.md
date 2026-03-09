# 部署说明

本文档说明如何在本地或服务器上运行 NBLM2PPTX 后端与前端。

## 本地开发

### 依赖

- **后端**：Python 3.11+，pip
- **前端**：Node.js 18+，npm 或 pnpm

### 后端

1. 进入后端目录并安装依赖：

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. 配置环境变量：

   ```bash
   cp .env.example .env
   # 编辑 .env，至少设置 GEMINI_API_KEY
   ```

3. 启动：

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   - API：<http://127.0.0.1:8000/docs>
   - 健康检查：<http://127.0.0.1:8000/health>

### 前端

1. 安装依赖并启动：

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. 浏览器访问 <http://localhost:5173>。前端会通过 Vite 代理将 `/api` 请求转发到后端（默认 `http://127.0.0.1:8000`），无需单独配置。

### 验证

按 [E2E_Verification.md](E2E_Verification.md) 执行：上传 PDF → 查看进度 → 导出 PPTX。

---

## 生产部署要点

- **后端**：使用 `uvicorn app.main:app --host 0.0.0.0 --port 8000`（去掉 `--reload`）；通过反向代理（Nginx/Caddy）挂 HTTPS。
- **前端**：执行 `npm run build`，将 `dist/` 交由静态服务器或与后端同一域名提供；若前后端不同域，需在后端设置正确的 `CORS_ORIGINS`。
- **环境变量**：在生产环境中设置 `GEMINI_API_KEY`、`UPLOAD_DIR`、`LOG_LEVEL` 等，不要提交 `.env`。

---

## Docker（可选）

仓库根目录提供 `docker-compose.yml`，用于一键启动后端并持久化上传目录与日志。

### 前置条件

- 已安装 Docker 与 Docker Compose（`docker-compose` 或 `docker compose` 均可）
- 在**项目根目录**准备 `.env`，至少设置 `GEMINI_API_KEY`（可复制 `backend/.env.example` 并重命名为 `.env`）

### 启动

```bash
# 项目根目录
docker compose up -d
```

- **后端**：<http://127.0.0.1:8000>，API 文档 <http://127.0.0.1:8000/docs>，健康检查 <http://127.0.0.1:8000/health>
- **前端**：在宿主机运行 `cd frontend && npm install && npm run dev`，访问 <http://localhost:5173>，前端通过 Vite 代理将 `/api` 转发到后端

### 卷与持久化

- 默认使用命名卷 `backend_uploads`、`backend_logs`，容器重启数据不丢失
- 若需直接访问宿主机目录，可在 `docker-compose.yml` 中把 volumes 改为 bind mount，例如：

  ```yaml
  volumes:
    - ./data/uploads:/app/uploads
    - ./data/logs:/app/logs
  ```

### 环境变量

通过根目录 `.env` 或 `environment` 传入，常用变量：`GEMINI_API_KEY`（必填）、`GEMINI_LAYOUT_MODEL`、`GEMINI_MAX_RPM`、`UPLOAD_DIR`、`LOG_LEVEL`、`CORS_ORIGINS`、`PIPELINE_MAX_WORKERS`。完整说明见 `backend/.env.example`。

### 仅构建镜像

```bash
docker compose build
# 或仅构建后端镜像
docker build -t slideforge-backend:latest ./backend
```

### 停止与清理

```bash
docker compose down
# 若需同时删除卷（会清空上传与日志）
docker compose down -v
```
