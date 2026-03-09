---
priority: 2
command_name: doc-gap-analysis
description: 文档缺口分析。基于 Memory ROOT 盘点现有文档，列出缺失与建议生成顺序。
---

# 文档缺口分析（/doc-gap-analysis）

执行**项目文档治理**中的缺口分析。必须先读取 Memory ROOT，再执行分析。

**Skill 路径约定**：优先从 `project-docs-governance/` 读取；若不存在则从 `.cursor/skills/project-docs-governance/` 读取（相对于使用方项目仓库根）。

## 1. 读取 Memory ROOT

- 优先读取 `.apm/Memory/Memory_Root.md`；若不存在则尝试 `docs/Memory_Root.md` 或询问用户。
- 吸收：项目目标、阶段、技术栈、是否为 AI 项目（是否需 AI 专项文档）。

## 2. 读取本 Skill 指引

- 读取 `project-docs-governance/SKILL.md`（若不存在则 `.cursor/skills/project-docs-governance/SKILL.md`）。
- 读取 `project-docs-governance/references/document-map.md`。

## 3. 执行缺口分析

- **盘点**：若存在 `docs/INDEX.md`，优先基于其中「已有」与「待补充」列表；否则扫描 `docs/`、仓库根、`.apm/`。列出已有文档（路径、类型、最后修改时间）。
- **应有文档**：按 document-map 与项目类型（常规 / AI 项目）列出应有文档类型；AI 项目需包含 document-map 中「AI 项目专项」所列类型。
- **缺口**：标出缺失、仅占位、明显过旧的文档及建议优先级。
- **建议生成顺序**：按依赖关系给出与 `/doc-generate` 一致的顺序，便于直接衔接生成：第一轮 项目概述、文档索引、术语表 → 第二轮 技术选型、环境说明、配置说明 → 第三轮 系统架构、部署手册 → 第四轮 运维、验收、测试计划、安全设计 → 第五轮 Onboarding、FAQ、监控、Runbook 索引、Release Notes、ADR。

## 4. 输出

- 输出 **缺口分析报告**（Markdown，含表格），**必须**包含：
  - **已有文档表**：路径、类型、状态（已有/占位/过旧）
  - **应有文档表**：document-map 类型、是否已有、缺口说明
  - **缺失与过旧列表**：带优先级（高/中/低）
  - **建议生成顺序**：表格或编号列表（与上一条一致），可直接作为 `/doc-generate` 的输入依据
  - **与 Memory ROOT 的对应**：项目阶段、是否 AI 项目、建议包含的文档范围

全部输出使用中文。
