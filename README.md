# SlideForge

将 PDF / 图片转为「背景图 + 可编辑文字」的 PPTX。本仓库为 **FastAPI 后端 + React 前端** 全栈实现，支持上传 PDF、实时进度、导出可编辑 PPTX。

> 灵感/参考自 [laihenyi/NBLM2PPTX](https://github.com/laihenyi/NBLM2PPTX)。

## 技术栈

- **后端**：FastAPI、PyMuPDF、Google Gemini（版面 OCR）、OpenCV（配色/去字）、python-pptx
- **前端**：React、Vite、WebSocket（进度）
- **流程**：PDF → 页图 → Gemini 版面解析 → 配色 / 裁剪 / 背景净化 → 合成 PPTX

## 目录结构

```
├── backend/          # FastAPI 服务
│   ├── app/
│   │   ├── api/v1/   # 上传、任务、导出、WebSocket
│   │   ├── core/     # 任务存储、日志
│   │   └── pipeline/ # PDF→图、OCR、配色、裁剪、去字、PPTX 合成
│   ├── tests/
│   └── requirements.txt
├── frontend/         # React 前端
│   ├── src/
│   └── package.json
├── docs/             # 文档与 API
│   ├── api/          # OpenAPI、Slide Schema
│   ├── degradation-strategy.md
│   ├── E2E_Verification.md
│   └── standards/    # 代码规范
└── .env.example      # 见 backend/.env.example
```

## 环境变量

后端配置见 `backend/.env.example`，复制为 `backend/.env` 后按需修改：

| 变量 | 说明 |
|------|------|
| `GEMINI_API_KEY` | **必填**。Gemini API Key，用于版面 OCR。 |
| `UPLOAD_DIR` | 上传与任务文件目录，默认 `./uploads`。 |
| `LOG_LEVEL` | 日志级别，默认 `INFO`。 |
| `GEMINI_LAYOUT_MODEL` | 可选，默认 `gemini-2.5-flash`。免费层 Gemini 2 Flash 额度为 0，须用 2.5 Flash。 |
| `GEMINI_MAX_RPM` | 可选，Gemini 每分钟请求上限；免费层 2.5 Flash 为 5，建议设为 `5`。 |
| `CORS_ORIGINS` | 可选，CORS 允许源。 |
| `MAX_FILE_SIZE` | 可选，上传大小限制（字节）。 |

## 快速开始

### Docker 一键运行（推荐，可分享给他人）

**前提**：已安装 [Docker](https://docs.docker.com/get-docker/)。

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/SlideForge.git && cd SlideForge

# 2. 设置 Gemini API Key 并运行
export GEMINI_API_KEY=你的API密钥
./scripts/run-docker.sh
```

或使用 docker-compose（适合后台常驻）：

```bash
# 在项目根目录创建 .env 文件，写入：GEMINI_API_KEY=你的API密钥
echo "GEMINI_API_KEY=你的API密钥" > .env
docker-compose up -d
```

- 访问：<http://127.0.0.1:8000>（前端 + API），API 文档：<http://127.0.0.1:8000/docs>。
- 上传与任务文件：`./uploads`（宿主机）。
- 构建镜像：`docker build -t slideforge:latest .`；可推送到 Docker Hub 供他人 `docker pull` 后直接运行。
- **预构建镜像**：推送到 `main` 分支后，GitHub Actions 会自动构建并推送到 `ghcr.io/bingooyong/slideforge:latest`，他人可直接 `docker pull ghcr.io/bingooyong/slideforge:latest` 运行。

### 本地一键打包启动

在仓库根目录执行一次脚本即可完成：检查/创建 `.env`、安装依赖（如需）、构建前端、启动后端（单端口同时提供 API + 前端）：

```bash
./scripts/build-and-serve.sh
```

- 首次运行若缺少 `backend/.env`，会从 `backend/.env.example` 复制，请编辑并填入 `GEMINI_API_KEY` 后再次执行。
- 启动后访问：<http://127.0.0.1:8000>（前端 + API），API 文档：<http://127.0.0.1:8000/docs>。
- 按 `Ctrl+C` 停止服务。

### 分步启动（开发时前后端分离）

#### 1. 后端

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入 GEMINI_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload
```

默认地址：<http://127.0.0.1:8000>，API 文档：<http://127.0.0.1:8000/docs>。

#### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

默认地址：<http://localhost:5173>，会代理 `/api` 到后端。

#### 3. 使用

打开前端地址 → 选择 PDF → 上传 → 等待进度完成 → 导出 PPTX。

#### 4. 任务文件与临时文件位置

所有任务相关文件都在后端配置的 **上传目录** 下，按任务 ID 分目录存放（由 `UPLOAD_DIR` 控制，默认 `./uploads`，相对后端进程工作目录）：

| 路径 | 说明 |
|------|------|
| `{UPLOAD_DIR}/tasks/{task_id}/input.pdf` | 上传的原始 PDF |
| `{UPLOAD_DIR}/tasks/{task_id}/output.pptx` | 流水线生成的 PPTX（任务成功时存在） |

例如默认在 `backend` 下启动时，任务 `2bc5c782-63e2-4b10-a8cd-67a05e250a6b` 对应：

- `backend/uploads/tasks/2bc5c782-63e2-4b10-a8cd-67a05e250a6b/input.pdf`
- `backend/uploads/tasks/2bc5c782-63e2-4b10-a8cd-67a05e250a6b/output.pptx`

中间产物（页图、OCR 结果等）仅在内存中处理，不落盘。如需清理旧任务，直接删除对应 `tasks/{task_id}` 目录即可。

## 文档与规范

- **文档索引**：[docs/INDEX.md](docs/INDEX.md)（按类型与角色列出的文档地图）
- **API**：[docs/api/openapi.yaml](docs/api/openapi.yaml)、[docs/api/slide-schema.json](docs/api/slide-schema.json)
- **代码规范**：[docs/Code_Standards.md](docs/Code_Standards.md)、[docs/standards/](docs/standards/)
- **产品需求**：[docs/PRD.md](docs/PRD.md)
- **端到端验证**：[docs/E2E_Verification.md](docs/E2E_Verification.md)
- **降级策略**：[docs/degradation-strategy.md](docs/degradation-strategy.md)

## Docker 启动（可选）

使用 Docker 可一键启动后端，适合演示或内网部署：

```bash
# 在项目根目录准备 .env（至少设置 GEMINI_API_KEY）
cp backend/.env.example .env
# 编辑 .env 填入 GEMINI_API_KEY

# 构建并启动后端
docker compose up -d

# 查看日志
docker compose logs -f backend
```

- **后端 API**：<http://127.0.0.1:8000>，文档 <http://127.0.0.1:8000/docs>
- **前端**：在宿主机执行 `cd frontend && npm run dev`，访问 <http://localhost:5173>，Vite 会将 `/api` 代理到 `http://127.0.0.1:8000`
- **数据持久化**：上传文件与日志通过 Docker 卷 `backend_uploads`、`backend_logs` 持久化；需宿主机目录可改为在 [docs/Deployment.md](docs/Deployment.md) 中所述的 bind mount。

停止：`docker compose down`。

## 本地部署

详见 [docs/Deployment.md](docs/Deployment.md)：依赖安装、`.env` 配置、启动命令。

## 故障排除

- **429 / Quota exceeded**：免费层下 **Gemini 2 Flash**（`gemini-2.0-flash`）额度为 **0**，需改用 **Gemini 2.5 Flash**：在 `backend/.env` 中设置 `GEMINI_LAYOUT_MODEL=gemini-2.5-flash`、`GEMINI_MAX_RPM=5`（免费约 5 RPM / 20 RPD）。[限额说明](https://ai.google.dev/gemini-api/docs/rate-limits)
- **SSL / gRPC：BAD_DECRYPT、DECRYPTION_FAILED_OR_BAD_RECORD_MAC**：多为代理或 VPN 对 HTTPS 的干扰。调用 Gemini 时请关闭系统/浏览器代理或 VPN，或在本机直连网络下运行后端。

## License

MIT
