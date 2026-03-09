# 服务端项目结构（FastAPI）

本规范约定 FastAPI 服务端目录组织、分层与配置方式，便于维护和扩展。

## 参考

- FastAPI 官方文档与社区实践：按领域/功能组织，路由薄、逻辑在服务层。
- 配置集中、依赖注入、统一异常与响应结构。

---

## 1. 推荐目录结构

按**领域/功能**组织，而非仅按“类型”（如把所有 router 放一起）：

```
backend/
├── app/
│   ├── main.py              # 应用入口，挂载路由与中间件
│   ├── config.py            # 配置（环境变量、常量）
│   ├── dependencies.py      # 公共依赖（DB、当前用户等）
│   ├── api/
│   │   ├── v1/
│   │   │   ├── router.py    # 或按模块拆：upload.py, tasks.py, export.py
│   │   │   └── ...
│   ├── core/                # 核心领域（或按业务拆：tasks/, pipeline/, export/）
│   │   ├── schemas.py       # Pydantic 请求/响应模型
│   │   ├── service.py       # 业务逻辑
│   │   ├── exceptions.py    # 领域内自定义异常
│   │   └── ...
│   └── pipeline/            # 流水线相关（解析、背景净化、PPTX 合成）
│       ├── schemas.py
│       ├── extract.py
│       ├── inpainting.py
│       └── pptx_build.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

- **api/**：只做 HTTP/WebSocket 入口、参数校验、调用 service、返回响应。
- **core / pipeline**：业务逻辑、第三方调用（Gemini、OpenCV、python-pptx）集中在此，便于单测与复用。
- **schemas**：与 API 契约、前端共享的 JSON Schema 对齐；优先 Pydantic 模型。

---

## 2. 分层约定

- **路由层 (router)**：解析请求、校验输入（Pydantic）、调用 service、处理 HTTP 异常并返回统一响应格式。
- **服务层 (service)**：编排业务流程、调用 pipeline、读写存储/队列；不直接依赖 FastAPI 类型。
- **配置**：从环境变量或配置文件读取，集中在 `config` 模块；敏感信息不写进代码。
- **依赖注入**：使用 FastAPI `Depends()` 注入 DB 会话、配置、当前任务等，便于测试与替换。

---

## 3. 错误与响应

- 使用统一错误处理（如 exception handler），将业务异常映射为固定结构的 HTTP 响应与状态码。
- 领域异常建议继承自公共基类，便于在 handler 中区分 4xx/5xx。
- 列表/分页等响应格式与前端约定一致（如 `{ "items": [], "total": 0 }`）。

---

## 4. 本地开发环境

- **Python 虚拟环境**：所有 Python 开发与运行必须在 **venv** 中进行（见 [Repository_Conventions.md](Repository_Conventions.md) 与 [CONTRIBUTING.md](../../CONTRIBUTING.md)）。推荐在仓库根目录创建 `.venv`，安装依赖：`pip install -r backend/requirements.txt`。

## 5. 本项目约定

- **应用工厂**：如需多环境或测试，可用 `create_app()` 构造 `FastAPI()`，在 `main.py` 中调用。
- **WebSocket**：进度推送等与 REST 共用认证与配置；消息格式与前端 Schema 一致。
- **后台任务**：首版使用 FastAPI `BackgroundTasks`；若后续引入 Celery/Redis，将长任务从路由中抽到独立 worker，API 只负责提交与查询状态。
