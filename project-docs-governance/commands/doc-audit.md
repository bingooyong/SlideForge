---
priority: 2
command_name: doc-audit
description: 文档审计。盘点文档、对照体系清单、检查与 Memory ROOT 一致性，输出审计报告。
---

# 文档审计（/doc-audit）

执行**项目文档治理**流程中的审计动作。必须先读取 Memory ROOT，再执行审计。

**Skill 路径约定**：优先从项目根下的 `project-docs-governance/` 读取；若不存在则从 `.cursor/skills/project-docs-governance/` 读取（路径均相对于使用方项目仓库根）。

## 1. 读取 Memory ROOT

- 优先读取 `.apm/Memory/Memory_Root.md`；若不存在则尝试 `docs/Memory_Root.md` 或询问用户。
- 吸收：项目目标、阶段、架构决策、技术栈、约束、术语。

## 2. 读取本 Skill 指引

- 读取 `project-docs-governance/SKILL.md`（若不存在则 `.cursor/skills/project-docs-governance/SKILL.md`）。
- 读取 `project-docs-governance/references/document-map.md` 作为文档体系清单。
- **必须**读取 `project-docs-governance/references/quality-checklist.md`，对关键文档（README、架构、部署、API、文档索引）执行清单中的相关检查项。

## 3. 执行审计

- **范围**：用户可指定路径；未指定时默认扫描 `docs/`、仓库根（README 等）、`.apm/` 中的 Markdown 与约定文档。若存在 `docs/INDEX.md`，优先以其所列文档为盘点基础并核对实际文件。
- **盘点**：列出已有文档及大致用途、最后修改时间。
- **对照**：按 document-map 的文档类型清单，按项目类型（常规 / 含 AI）勾选应有文档，标出**缺失**、**仅占位**、**过旧**。
- **一致性**：检查与 Memory ROOT、术语表的一致性；检查交叉引用是否有效。
- **冲突**：若发现与 Memory ROOT 或其它文档冲突，在报告中明确列出并给出处理建议。

## 4. 输出

- 输出一份 **Markdown 审计报告**（结构化，便于后续跟进），**必须**包含：
  - **已有文档清单**：表格，列路径、用途、最后更新、与 document-map 类型对应
  - **缺失文档列表**：表格或列表，带建议优先级（高/中/低）
  - **过时/占位文档**：列出并给出建议（补全或重写）
  - **与 Memory ROOT 或术语表冲突项**：逐条列出并给出处理建议
  - **交叉引用失效项**：失效链接或指向不存在的文档
  - **quality-checklist 检查结果**：对关键文档的不通过项（若有）
  - **后续建议**：先生成/补全哪些、建议执行 `/doc-generate` 或 `/doc-sync` 的范围

全部输出使用中文。
