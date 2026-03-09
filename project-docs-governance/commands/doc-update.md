---
priority: 2
command_name: doc-update
description: 文档增量更新。根据变更原因（架构/接口/发布/事故等）确定受影响文档并做增量更新。
---

# 文档增量更新（/doc-update）

执行**项目文档治理**中的增量更新。必须先读取 Memory ROOT 与现有文档，再更新。

**Skill 路径约定**：优先从 `project-docs-governance/` 读取；若不存在则从 `.cursor/skills/project-docs-governance/` 读取（相对于使用方项目仓库根）。

## 1. 读取 Memory ROOT

- 优先读取 `.apm/Memory/Memory_Root.md`；若不存在则尝试 `docs/Memory_Root.md` 或询问用户。
- 若本次变更来自 Memory ROOT 更新，以 Memory 为准；否则更新后建议用户同步 Memory（若适用）。

## 2. 读取本 Skill 与文档地图

- 读取 `project-docs-governance/SKILL.md`（若不存在则 `.cursor/skills/project-docs-governance/SKILL.md`）。
- 读取 `project-docs-governance/references/document-map.md`（依赖与同步策略、更新触发规则）。

## 3. 确定变更原因与受影响文档

- **用户输入**：用户应说明变更原因；若用户只输入 `/doc-update` 未说明原因，**先询问**变更原因或让用户从下列类型中选择：架构变更、接口/API 变更、发布/版本、事故/复盘、其他（请简述）。再根据原因确定受影响文档。
- **映射**：按 document-map 的更新触发规则确定受影响文档，例如：
  - 架构变更 → 架构、详细设计、部署、运维、Runbook 中受影响部分
  - 接口变更 → API 文档、调用方说明、详细设计
  - 发布 → Release Notes、部署手册中的版本号
  - 事故/复盘 → Runbook、监控、运维、故障处理

## 4. 执行增量更新

- 在**已有文档**上补章节、改表述、更新引用；不整篇重写除非用户明确要求。
- 与 Memory ROOT 事实性一致；冲突时先提示并给出处理建议（以 Memory 为准 / 以用户为准 / 建议更新 Memory）。
- 每份更新后注明版本/状态/变更摘要；交叉引用与术语保持统一。

## 5. 输出

- 列出**更新后的文件**及**每份的变更摘要**。
- 建议是否将本次变更同步到 Memory ROOT（如架构决策、阶段状态）。

全部输出使用中文。
