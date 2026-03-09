# 端到端联调验证指南

本文档描述如何验证「PDF 上传 → 实时进度 → 导出 PPTX」全流程及错误路径。

## 前置条件

1. **GEMINI_API_KEY**：在 `backend/.env` 中配置有效的 Gemini API Key：
   ```bash
   cp backend/.env.example backend/.env
   # 编辑 backend/.env，填入 GEMINI_API_KEY
   ```

2. **依赖安装**：
   ```bash
   cd backend && pip install -r requirements.txt
   cd frontend && npm install
   ```

## 启动服务

```bash
# 终端 1：启动后端（默认 http://127.0.0.1:8000）
cd backend && uvicorn app.main:app --reload

# 终端 2：启动前端（默认 http://localhost:5173，代理 /api 到后端）
cd frontend && npm run dev
```

## 正向流程验证

1. 打开 http://localhost:5173
2. 选择 3–5 页的 PDF 文件
3. 点击「开始上传」
4. 验证：
   - 获得 taskId
   - 进度条显示阶段：上传中 → 处理中 → 合成中 → 已完成
   - 百分比与当前页数正确更新
   - 任务完成后「导出 PPTX」按钮可用
5. 点击「导出 PPTX」，下载文件
6. 用 PowerPoint 或 WPS 打开，检查：
   - 文字可编辑
   - 位置与原文接近
   - 背景去字效果可接受
   - 图片块正确插入

## 错误路径验证

### 无效 GEMINI_API_KEY

1. 在 `backend/.env` 中设置 `GEMINI_API_KEY=invalid_key`
2. 重启后端
3. 上传 PDF
4. 验证：任务标记为失败，前端显示「任务处理失败，请检查 GEMINI_API_KEY 或稍后重试。」

### 损坏/加密 PDF

1. 上传非 PDF 文件（如 .txt 改名为 .pdf）或加密 PDF
2. 验证：上传阶段返回 400/500，前端显示明确错误信息

### 导出未完成任务

1. 上传后立即点击「导出 PPTX」（任务仍在处理中）
2. 验证：按钮应处于禁用状态；若通过其他方式请求，应返回 202 或相应提示

## WebSocket 消息格式

进度消息包含 `status` 字段以区分完成与失败：

- `status: "completed"`：任务成功完成
- `status: "failed"`：任务失败（如 API Key 无效、超时等）

前端据此更新 UI 并显示错误提示。
