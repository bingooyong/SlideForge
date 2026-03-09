# NBLM2PPTX 代码与仓库规范

本仓库采用业内常用最佳实践，并在此基础上做项目内统一约定。所有贡献与实现应遵循以下规范。

## 规范文档索引

| 文档 | 说明 |
|------|------|
| [standards/Python_Style_Guide.md](standards/Python_Style_Guide.md) | 服务端 Python 风格（PEP 8 + Google 要点）、类型注解、格式化工具 |
| [standards/Frontend_Style_Guide.md](standards/Frontend_Style_Guide.md) | 前端 React + TypeScript 结构、组件约定、目录与命名 |
| [standards/Backend_Structure.md](standards/Backend_Structure.md) | FastAPI 项目结构、路由/服务分层、配置与依赖 |
| [standards/Repository_Conventions.md](standards/Repository_Conventions.md) | 仓库级约定：README、CONTRIBUTING、分支、提交信息、PR |

## 本项目技术栈与工具约定

- **服务端**：Python 3.11+，FastAPI；格式化推荐 Black；类型检查可选用 pyright 或 mypy。
- **前端**：React 18+，TypeScript，Vite，Zustand；ESLint + Prettier 统一风格。
- **API**：REST + WebSocket；请求/响应与事件结构以 Schema 为准，见 API 契约文档。

## 优先级

1. 本目录下 `standards/*.md` 中的约定优先于外部参考。
2. 外部参考（PEP 8、Google Python Style、React TypeScript Style Guide 等）用于补充未在项目规范中细化的部分。
