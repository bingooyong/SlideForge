# SlideForge 全栈镜像：前端构建 + 后端 API，单端口提供完整服务
# 构建：docker build -t slideforge:latest .
# 运行：docker run -p 8000:8000 -e GEMINI_API_KEY=你的Key slideforge:latest

# ========== 阶段 1：构建前端 ==========
FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ========== 阶段 2：构建后端依赖 ==========
FROM python:3.12-slim AS backend-builder
WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ========== 阶段 3：运行镜像 ==========
FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 复制后端依赖
COPY --from=backend-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制后端代码
COPY backend/app ./app

# 复制前端构建产物到 static（供 FastAPI 挂载）
COPY --from=frontend-builder /build/dist ./static

# 持久化目录
RUN mkdir -p /app/uploads /app/logs

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
