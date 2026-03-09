# NBLM2PPTX 文档索引 / 文档地图

**文档版本**：v1.0  
**状态**：draft  
**最后更新**：2026-03-07  
**说明**：本项目正式文档列表，用于导航与缺口检查。与项目文档治理 document-map 体系一致。

---

## 按文档类型

| 文档 | 路径 | 主要读者 | 状态 |
|------|------|----------|------|
| README | [README](../README.md) | 所有人 | approved |
| 项目概述 | [project-overview.md](project-overview.md) | 产品、PM、架构 | draft |
| 文档索引 | 本文档 | 所有人 | draft |
| 术语表 | [glossary.md](glossary.md) | 全员 | draft |
| 产品需求（PRD） | [PRD.md](PRD.md)、[PRD-zh.md](PRD-zh.md) | 产品、PM、开发 | approved |
| 详细设计 | [Design.md](Design.md) | 开发、测试 | approved |
| 部署手册 | [Deployment.md](Deployment.md) | 运维、发布 | approved |
| API / Schema | [api/openapi.yaml](api/openapi.yaml)、[api/slide-schema.json](api/slide-schema.json)、[Slide-Schema-V2.md](Slide-Schema-V2.md) | 开发、测试 | approved |
| 降级策略 | [degradation-strategy.md](degradation-strategy.md) | 开发、运维 | approved |
| 端到端验证 | [E2E_Verification.md](E2E_Verification.md) | 测试、开发 | approved |
| 代码与仓库规范 | [Code_Standards.md](Code_Standards.md)、[standards/](standards/) | 开发 | approved |
| 系统架构 | [architecture.md](architecture.md) | 架构、开发、运维 | draft |
| 技术选型 | [tech-stack.md](tech-stack.md) | 架构、开发 | draft |
| 环境说明 | [environments.md](environments.md) | 开发、运维 | draft |
| 配置说明 | [configuration.md](configuration.md) | 开发、运维 | draft |
| 运维/操作手册 | [operations.md](operations.md) | 运维 | draft |
| 监控与告警 | [monitoring.md](monitoring.md) | 运维 | draft |
| Runbook | [runbooks/](runbooks/) | 运维、值班 | draft（索引已建，单则待补） |
| 测试计划 | [testing-plan.md](testing-plan.md) | 测试、PM | draft |
| 验收标准/UAT | [acceptance.md](acceptance.md) | 产品、测试 | draft |
| 安全设计 | [security.md](security.md) | 架构、安全 | draft |
| Release Notes | [releases/](releases/) 或 CHANGELOG | 全员 | draft（目录与说明已建） |
| ADR | [adr/](adr/) | 架构、开发 | draft（ADR-001 已建） |
| FAQ | [faq.md](faq.md) | 全员 | draft |
| Onboarding | [onboarding.md](onboarding.md) | 新成员 | draft |

---

## 按角色

- **开发**：README、[Design.md](Design.md)、[PRD.md](PRD.md)、[api/](api/)、[Code_Standards.md](Code_Standards.md)、[standards/](standards/)、[Deployment.md](Deployment.md)、[E2E_Verification.md](E2E_Verification.md)、[degradation-strategy.md](degradation-strategy.md)、[project-overview.md](project-overview.md)、[glossary.md](glossary.md)、[architecture.md](architecture.md)、[tech-stack.md](tech-stack.md)、[environments.md](environments.md)、[configuration.md](configuration.md)。
- **运维**：[Deployment.md](Deployment.md)、[E2E_Verification.md](E2E_Verification.md)、[environments.md](environments.md)、[operations.md](operations.md)、[monitoring.md](monitoring.md)、[runbooks/](runbooks/)。
- **测试**：[E2E_Verification.md](E2E_Verification.md)、[api/](api/)、[PRD.md](PRD.md)、[testing-plan.md](testing-plan.md)、[acceptance.md](acceptance.md)、[environments.md](environments.md)。
- **产品/PM**：[PRD.md](PRD.md)、[PRD-zh.md](PRD-zh.md)、[project-overview.md](project-overview.md)、[acceptance.md](acceptance.md)、[releases/](releases/)、[faq.md](faq.md)。

---

## 上游与依赖

- 文档依赖与同步策略参见项目文档治理 document-map；本索引按「文档类型清单」整理，缺失项已标为「待补充」。
- 与 [Memory ROOT](../.apm/Memory/Memory_Root.md) 一致：Phase 01–04 已完成，项目发布就绪；技术栈 FastAPI + React，流水线含 Gemini 版面/OCR、OpenCV、python-pptx。

---

## 变更记录

| 日期       | 版本 | 变更摘要     |
|------------|------|--------------|
| 2026-03-07 | v1.0 | 初稿，基于现有 docs/ 与 document-map 盘点 |
| 2026-03-07 | v1.1 | 按 project-docs-governance 补全项目概述、术语表、技术选型、架构、环境、配置、运维、验收、测试计划、Onboarding、FAQ、安全、ADR、releases/runbooks/monitoring 占位；更新按角色索引 |
