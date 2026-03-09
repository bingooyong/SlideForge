# NBLM2PPTX

將 PDF / 圖片轉為「背景圖 + 可編輯文字」的 PPTX。本倉庫為 **FastAPI 後端 + React 前端** 全棧實現，支援上傳 PDF、即時進度、匯出可編輯 PPTX。

> 靈感/參考自 [laihenyi/NBLM2PPTX](https://github.com/laihenyi/NBLM2PPTX)。

[中文](README.md) | [简体中文](README-zh-CN.md) | [English](README.md) | [日本語](README-ja.md) | [Español](README-es.md) | [Français](README-fr.md)

## 技術棧

- **後端**：FastAPI、PyMuPDF、Google Gemini（版面 OCR）、OpenCV（配色/去字）、python-pptx
- **前端**：React、Vite、WebSocket（進度）
- **流程**：PDF → 頁圖 → Gemini 版面解析 → 配色 / 裁剪 / 背景淨化 → 合成 PPTX

## 快速開始

### Docker 一鍵執行（推薦）

```bash
export GEMINI_API_KEY=你的API密鑰
./scripts/run-docker.sh
```

### 本機一鍵啟動

```bash
./scripts/build-and-serve.sh
```

首次執行若缺少 `backend/.env`，會從 `backend/.env.example` 複製，請編輯並填入 `GEMINI_API_KEY` 後再次執行。啟動後存取 <http://127.0.0.1:8000>，API 文件 <http://127.0.0.1:8000/docs>。

### 分步啟動（開發）

```bash
# 後端
cd backend && cp .env.example .env && pip install -r requirements.txt && uvicorn app.main:app --reload

# 前端（另開終端）
cd frontend && npm install && npm run dev
```

## 環境變數

| 變數 | 說明 |
|------|------|
| `GEMINI_API_KEY` | **必填**。Gemini API Key，用於版面 OCR。 |
| `UPLOAD_DIR` | 上傳與任務檔案目錄，預設 `./uploads`。 |
| `GEMINI_LAYOUT_MODEL` | 可選，預設 `gemini-2.5-flash`。 |
| `GEMINI_MAX_RPM` | 可選，免費層 2.5 Flash 建議 `5`。 |

完整說明見 [README.md](README.md)。文件與規範見 [docs/INDEX.md](docs/INDEX.md)。
