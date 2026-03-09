# NBLM2PPTX

将 PDF / 图片转为「背景图 + 可编辑文字」的 PPTX。本仓库为 **FastAPI 后端 + React 前端** 全栈实现，支持上传 PDF、实时进度、导出可编辑 PPTX。

> 灵感/参考自 [laihenyi/NBLM2PPTX](https://github.com/laihenyi/NBLM2PPTX)。

[中文](README.md) | [繁體中文](README-zh-TW.md) | [English](README.md) | [日本語](README-ja.md) | [Español](README-es.md) | [Français](README-fr.md)

## 技术栈

- **后端**：FastAPI、PyMuPDF、Google Gemini（版面 OCR）、OpenCV（配色/去字）、python-pptx
- **前端**：React、Vite、WebSocket（进度）
- **流程**：PDF → 页图 → Gemini 版面解析 → 配色 / 裁剪 / 背景净化 → 合成 PPTX

## 快速开始

### Docker 一键运行（推荐）

```bash
export GEMINI_API_KEY=你的API密钥
./scripts/run-docker.sh
```

### 本地一键启动

```bash
./scripts/build-and-serve.sh
```

首次运行若缺少 `backend/.env`，会从 `backend/.env.example` 复制，请编辑并填入 `GEMINI_API_KEY` 后再次执行。启动后访问 <http://127.0.0.1:8000>，API 文档 <http://127.0.0.1:8000/docs>。

### 分步启动（开发）

```bash
# 后端
cd backend && cp .env.example .env && pip install -r requirements.txt && uvicorn app.main:app --reload

# 前端（另开终端）
cd frontend && npm install && npm run dev
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `GEMINI_API_KEY` | **必填**。Gemini API Key，用于版面 OCR。 |
| `UPLOAD_DIR` | 上传与任务文件目录，默认 `./uploads`。 |
| `GEMINI_LAYOUT_MODEL` | 可选，默认 `gemini-2.5-flash`。 |
| `GEMINI_MAX_RPM` | 可选，免费层 2.5 Flash 建议 `5`。 |

完整说明见 [README.md](README.md)。文档与规范见 [docs/INDEX.md](docs/INDEX.md)。
