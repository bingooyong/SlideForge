---
priority: 2
command_name: doc-runbook-create
description: 创建单则 Runbook。根据故障现象或告警名称按模板生成 Runbook 并与索引衔接。
---

# 创建 Runbook（/doc-runbook-create）

执行**项目文档治理**中的 Runbook 创建。必须先读取 Memory ROOT 与现有运维/监控文档，再生成。

**Skill 路径约定**：优先从 `project-docs-governance/` 读取；若不存在则从 `.cursor/skills/project-docs-governance/` 读取（相对于使用方项目仓库根）。

## 1. 读取 Memory ROOT

- 优先读取 `.apm/Memory/Memory_Root.md`；若不存在则尝试 `docs/Memory_Root.md` 或询问用户。
- 吸收：服务/组件名称、架构要点，确保 Runbook 中组件名与架构、运维文档一致。

## 2. 读取本 Skill 与模板

- 读取 `project-docs-governance/SKILL.md`（若不存在则 `.cursor/skills/project-docs-governance/SKILL.md`）。
- 读取 `project-docs-governance/references/operations-guide.md`（Runbook 部分）。
- 读取 `project-docs-governance/templates/runbook-template.md`。

## 3. 确定输入

- **用户输入**：故障现象或告警名称；可选：已有监控/运维文档路径（如 `docs/monitoring.md`、`docs/runbooks/`）。
- 若用户未给现象/告警名，**先询问**再生成。

## 4. 生成 Runbook

- 若 `docs/runbooks/` 不存在，**先创建**该目录并在其中创建 `README.md` 作为 Runbook 索引（见 templates/docs-index 或 operations-guide 中 Runbook 索引结构），再写入单则 Runbook；若已存在索引，在输出中给出索引更新建议（应添加的条目）。

- 按 runbook-template 结构填写：故障现象、可能原因、诊断步骤、处理步骤、若无法解决（升级、临时缓解）、相关文档、变更记录。
- 服务/组件名与架构、运维文档一致；步骤可执行；与现有 Runbook 索引（如 `docs/runbooks/README.md`）衔接，或在输出中建议索引更新。

## 5. 输出

- **新建 Runbook 文件路径**（建议放在 `docs/runbooks/` 下，文件名与现象/告警相关）。
- **索引更新建议**：若存在 Runbook 索引，给出应添加的条目或修改建议。

全部输出使用中文。
