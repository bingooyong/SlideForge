---
priority: 2
command_name: doc-sync
description: 文档同步。在选定文档间统一术语、修正交叉引用、对齐版本与状态，与 Memory ROOT 一致。
---

# 文档同步（/doc-sync）

执行**项目文档治理**中的文档同步。必须先读取 Memory ROOT，再执行同步。

**Skill 路径约定**：优先从 `project-docs-governance/` 读取；若不存在则从 `.cursor/skills/project-docs-governance/` 读取（相对于使用方项目仓库根）。

## 1. 读取 Memory ROOT

- 优先读取 `.apm/Memory/Memory_Root.md`；若不存在则尝试 `docs/Memory_Root.md` 或询问用户。
- 吸收：项目状态、术语、版本相关表述，作为同步的权威来源。

## 2. 读取本 Skill 指引

- 读取 `project-docs-governance/SKILL.md`（若不存在则 `.cursor/skills/project-docs-governance/SKILL.md`）。
- 读取 `project-docs-governance/references/document-map.md`（依赖与同步策略）。

## 3. 确定同步范围

- **用户指定**：若用户给定了文档列表或路径，仅在这些文档间同步。
- **全部**：若用户说「全部」或**未指定**，按下列方式确定范围：若存在 `docs/INDEX.md`，以其中列出的所有文档路径为「全部」；否则扫描 `docs/` 下所有 Markdown 及仓库根 README。确保不遗漏文档索引中已登记的文档。
- **同步维度**：术语 / 交叉引用 / 版本与状态 / 与 Memory ROOT 表述对齐；用户可指定维度或默认**全部**。

## 4. 执行同步

- **术语**：以术语表（如 `docs/glossary.md`）为权威；在选定文档中统一替换为术语表表述；新术语先入术语表再使用。
- **交叉引用**：修正或补全相对路径链接；确保指向的文档存在且路径正确。
- **版本与状态**：对齐版本号、状态（draft/reviewed/approved）、最后更新时间；与 Release Notes 一致处保持一致。
- **与 Memory ROOT**：项目目标、阶段、技术栈等表述与 Memory ROOT 一致。

## 5. 输出

- 列出**变更的文件**及每份的**同步项说明**（例如：术语统一 3 处、修正链接 2 处、版本对齐 1 处）。
- 若发现与 Memory ROOT 冲突，先提示并给出建议再执行。

全部输出使用中文。
