# NBLM2PPTX

PDF または画像を「背景画像 + 編集可能なテキスト」の PPTX に変換します。本リポジトリは **FastAPI バックエンド + React フロントエンド** のフルスタック実装で、PDF アップロード、リアルタイム進捗、編集可能な PPTX のエクスポートをサポートします。

> 灵感/参考自 [laihenyi/NBLM2PPTX](https://github.com/laihenyi/NBLM2PPTX)。

[中文](README.md) | [简体中文](README-zh-CN.md) | [繁體中文](README-zh-TW.md) | [日本語](README-ja.md) | [Español](README-es.md) | [Français](README-fr.md)

## 技術スタック

- **バックエンド**: FastAPI、PyMuPDF、Google Gemini（レイアウト OCR）、OpenCV（配色/トリミング）、python-pptx
- **フロントエンド**: React、Vite、WebSocket（進捗）
- **フロー**: PDF → ページ画像 → Gemini レイアウト解析 → 配色/トリミング/背景クリーンアップ → PPTX 合成

## クイックスタート

### Docker（推奨）

```bash
export GEMINI_API_KEY=あなたのAPIキー
./scripts/run-docker.sh
```

### ローカル一括起動

```bash
./scripts/build-and-serve.sh
```

`backend/.env` がない場合は `backend/.env.example` からコピーされます。編集して `GEMINI_API_KEY` を設定し、再度実行してください。起動後は <http://127.0.0.1:8000>、API ドキュメントは <http://127.0.0.1:8000/docs>。

### 手順別起動（開発時）

```bash
# バックエンド
cd backend && cp .env.example .env && pip install -r requirements.txt && uvicorn app.main:app --reload

# フロントエンド（別ターミナル）
cd frontend && npm install && npm run dev
```

## 環境変数

| 変数 | 説明 |
|------|------|
| `GEMINI_API_KEY` | **必須**。レイアウト OCR 用 Gemini API キー。 |
| `UPLOAD_DIR` | アップロード・タスク用ディレクトリ、デフォルト `./uploads`。 |
| `GEMINI_LAYOUT_MODEL` | 任意、デフォルト `gemini-2.5-flash`。 |
| `GEMINI_MAX_RPM` | 任意。無料枠 2.5 Flash では `5` を推奨。 |

詳細は [README.md](README.md)。ドキュメント索引は [docs/INDEX.md](docs/INDEX.md)。
