---
priority: 2
command_name: doc-release-check
description: 发布前文档检查。检查 Release Notes、部署版本、API 变更、链接与质量清单关键项。
---

# 发布前文档检查（/doc-release-check）

执行**项目文档治理**中的发布前文档门禁。必须先读取 Memory ROOT，再执行检查。

**Skill 路径约定**：优先从 `project-docs-governance/` 读取；若不存在则从 `.cursor/skills/project-docs-governance/` 读取（相对于使用方项目仓库根）。

## 1. 读取 Memory ROOT

- 优先读取 `.apm/Memory/Memory_Root.md`；若不存在则尝试 `docs/Memory_Root.md` 或询问用户。
- 确认当前阶段与版本预期，与检查结果对照。

## 2. 读取本 Skill 与质量清单

- 读取 `project-docs-governance/SKILL.md`（若不存在则 `.cursor/skills/project-docs-governance/SKILL.md`）。
- 读取 `project-docs-governance/references/quality-checklist.md`。

## 3. 确定版本

- 用户可指定版本号或发布标签。**若未指定**：优先从 Memory ROOT 中阶段/版本表述推断；若无则从当前 Git 分支名或标签推断；仍无法推断时在输出中说明「未指定版本，以下检查以“当前发布”为假设」并继续执行。

## 4. 执行检查

- **必须**执行下列检查（不省略）：
  - **Release Notes / CHANGELOG**：是否包含本版本；变更描述是否与本次发布一致。
  - **部署手册**：版本号或适用版本是否更新；与 Release Notes 对应。
  - **API 文档**：若有破坏性变更，是否在 API 文档与 Release Notes 中说明。
  - **文档索引与 README**：文档索引（如 docs/INDEX.md）是否存在；README 中文档链接是否有效、无 404。
  - **quality-checklist**：对发布相关文档**必须**执行 `quality-checklist.md` 中与发布相关的全部项（元数据、版本一致性、交叉引用有效、无明文敏感信息等），并在输出中列出不通过项。

## 5. 输出

- **通过项**与**不通过项**列表；不通过项附**修复建议**。
- 若全部通过，可注明「建议通过文档门禁」；否则注明需修复后再检查。

全部输出使用中文。
