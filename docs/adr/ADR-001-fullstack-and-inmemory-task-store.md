# ADR-001：全栈 FastAPI + React 与内存任务存储

**状态**：accepted  
**日期**：2026-03-07  
**相关文档**：[项目概述](../project-overview.md)、[架构设计](../architecture.md)、[技术选型](../tech-stack.md)

---

## 背景与问题

- 产品目标为将 PDF/图片转为可编辑 PPTX；PRD 中曾描述「纯前端、零部署」形态，但需要可落地、可维护、可扩展的实现。
- 需确定：服务端是否参与、任务状态如何存储、前后端边界。

## 决策

- 采用 **FastAPI 后端 + React 前端** 全栈形态：后端负责上传存储、流水线（PDF→页图→Gemini→OpenCV→python-pptx）、任务状态与导出；前端负责上传/选页/进度/导出 UI。
- 任务状态首版采用 **InMemoryTaskStore**（内存），不持久化；重启后任务列表清空，适合单机演示与迭代。

## 选项与权衡

- **纯前端**：无需后端，但 PDF 解析、Gemini 调用、PPTX 合成均在浏览器，受限于配额、性能与包体积；API Key 存前端有泄露风险。
- **全栈 + 内存存储**：后端集中管理 Key 与流水线，前端只做 UI；内存存储实现简单，无数据库依赖，代价是重启丢失、无法多实例共享状态。
- **全栈 + Redis/DB**：可持久化、多实例，留作后续演进；首版不引入以降低复杂度。

## 后果

- **正面**：部署简单、与 Memory ROOT 及当前实现一致；流水线可单测、可替换。
- **负面**：重启后任务不可恢复；多实例需后续引入共享存储。
- **后续**：若需持久化或多实例，可新增 ADR 将 TaskStore 换为 Redis 或 DB。

## 相关

- [.apm/Memory/Memory_Root.md](../../.apm/Memory/Memory_Root.md)、Phase 02 Task Logs
