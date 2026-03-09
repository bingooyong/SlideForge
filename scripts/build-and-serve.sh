#!/usr/bin/env bash
# 一键：安装依赖（可选）、构建前端、启动后端（单端口提供 API + 前端）
# 用法：从仓库根目录执行 ./scripts/build-and-serve.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[1/4] 检查后端 .env ..."
if [[ ! -f backend/.env ]]; then
  if [[ -f backend/.env.example ]]; then
    echo "  未找到 backend/.env，已从 .env.example 复制，请编辑并填入 GEMINI_API_KEY。"
    cp backend/.env.example backend/.env
  else
    echo "  错误：缺少 backend/.env，请先创建并配置 GEMINI_API_KEY。"
    exit 1
  fi
fi

echo "[2/4] 后端 Python 环境 ..."
if [[ -z "${VIRTUAL_ENV:-}" ]] && [[ -d "$ROOT/.venv" ]]; then
  source "$ROOT/.venv/bin/activate"
fi
if ! command -v uvicorn &>/dev/null; then
  echo "  未检测到 uvicorn，正在安装后端依赖..."
  pip install -r backend/requirements.txt
fi

echo "[3/4] 构建前端 ..."
if [[ ! -d frontend/node_modules ]]; then
  echo "  首次运行：安装前端依赖..."
  (cd frontend && npm install)
fi
(cd frontend && npm run build)
rm -rf backend/static
cp -r frontend/dist backend/static
echo "  已输出到 backend/static"

echo "[4/4] 启动后端（API + 静态前端）..."
echo "  访问: http://127.0.0.1:8000"
echo "  API 文档: http://127.0.0.1:8000/docs"
echo "  按 Ctrl+C 停止"
cd backend && exec uvicorn app.main:app --host 0.0.0.0 --port 8000
