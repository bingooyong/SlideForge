# NBLM2PPTX 术语表

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**说明**：项目内统一术语，供各文档引用。

---

## 产品与形态

| 术语 | 定义 | 备注 |
|------|------|------|
| NBLM2PPTX | 本仓库项目名：将 PDF/图片转为可编辑 PPTX 的全栈应用 | 后端 FastAPI + 前端 React |
| 可编辑 PPTX | 背景为图、文字为可编辑文本框的 PowerPoint 格式 | 与“整页为图”的 PPT 区分 |
| 按页降级 | 流水线中某一页失败时，该页标记为失败或占位，不阻塞其余页生成 | 见 [degradation-strategy.md](degradation-strategy.md) |
| Lite / Standard | PRD 中的两种 OCR 模式：Lite 速度/配额优先、Standard 样式还原优先 | 本仓库实现中对应 pipeline 与 Schema 的简化/完整形态 |

## 流水线与组件

| 术语 | 定义 | 备注 |
|------|------|------|
| 流水线 / Pipeline | 从 PDF/图片到 PPTX 的完整处理链 | PDF→页图→Gemini 版面/OCR→OpenCV 配色/裁剪→背景净化→python-pptx 合成 |
| 版面 / Layout | 页面上文字块、图片块的位置与层级结构 | 由 Gemini 版面分析得到 |
| OCR | 光学字符识别，此处指 Gemini 返回的文本与坐标（及可选样式） | 用于生成可编辑文字框 |
| 主题色 / 配色 | 从页面提取的主色、背景色及 3–5 个主题色（hex） | OpenCV 提取，用于 PPTX 配色板 |
| 背景净化 | 去除或弱化背景中的文字，保留版面与图形 | 本仓库中由流水线环节实现 |
| Slide Schema | 单页幻灯片的 JSON 结构：尺寸、背景、blocks、主题色等 | 见 [api/slide-schema.json](api/slide-schema.json) |
| Task / 任务 | 一次上传对应的处理单元，含 task_id、状态、进度、结果路径 | 后端 InMemoryTaskStore 管理 |

## 技术栈

| 术语 | 定义 | 备注 |
|------|------|------|
| FastAPI | 后端 Web 框架 | 提供 REST、WebSocket、后台任务 |
| WebSocket | 实时推送任务进度（page_index、total_pages、stage、progress） | 端点见 API 文档 |
| InMemoryTaskStore | 当前版本的任务状态存储，内存存储、不持久化 | 可扩展为持久化存储 |
| Gemini | Google 大模型 API，用于版面分析与 OCR | 需 GEMINI_API_KEY |
| python-pptx | Python 库，用于生成 PPTX 文件 | 后端合成单页与整份 PPTX |

## 文档与流程

| 术语 | 定义 | 备注 |
|------|------|------|
| Memory ROOT | 项目长期记忆与上下文基线（APM） | `.apm/Memory/Memory_Root.md` |
| PRD | 产品需求文档 | [PRD.md](PRD.md)、[PRD-zh.md](PRD-zh.md) |
| E2E | 端到端（End-to-End） | 见 [E2E_Verification.md](E2E_Verification.md) |

---

## 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿，覆盖产品、流水线、技术栈与文档术语 |
