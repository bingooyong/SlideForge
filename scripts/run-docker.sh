#!/usr/bin/env bash
# 一键构建并运行 SlideForge Docker 镜像
# 用法：
#   export GEMINI_API_KEY=你的API密钥
#   ./scripts/run-docker.sh
# 或：
#   GEMINI_API_KEY=你的API密钥 ./scripts/run-docker.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

IMAGE_NAME="${SLIDEFORGE_IMAGE:-slideforge:latest}"
CONTAINER_NAME="${SLIDEFORGE_CONTAINER:-slideforge}"

# 从环境变量或 .env 读取 GEMINI_API_KEY
if [[ -z "${GEMINI_API_KEY:-}" ]] && [[ -f backend/.env ]]; then
  export $(grep -E '^GEMINI_API_KEY=' backend/.env | xargs)
fi

if [[ -z "${GEMINI_API_KEY:-}" ]]; then
  echo "错误：请设置 GEMINI_API_KEY 环境变量。"
  echo "  示例：export GEMINI_API_KEY=AIza..."
  echo "  或：在 backend/.env 中配置 GEMINI_API_KEY"
  exit 1
fi

echo "构建镜像: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

mkdir -p "$ROOT/uploads"

echo ""
echo "启动容器: $CONTAINER_NAME"
echo "  访问: http://127.0.0.1:8000"
echo "  API 文档: http://127.0.0.1:8000/docs"
echo "  上传与任务文件: $ROOT/uploads"
echo "  按 Ctrl+C 停止"
echo ""

docker run --rm -it \
  --name "$CONTAINER_NAME" \
  -p 8000:8000 \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  -e UPLOAD_DIR=/app/uploads \
  -e GEMINI_LAYOUT_MODEL="${GEMINI_LAYOUT_MODEL:-gemini-2.5-flash}" \
  -e GEMINI_MAX_RPM="${GEMINI_MAX_RPM:-5}" \
  -e CORS_ORIGINS="${CORS_ORIGINS:-*}" \
  -v "$ROOT/uploads:/app/uploads" \
  "$IMAGE_NAME"
