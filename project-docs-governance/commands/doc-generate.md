---
priority: 2
command_name: doc-generate
description: 生成或补全项目文档。未指定类型时按缺口与依赖顺序生成全部缺失文档；指定时仅处理该项。与「按 project-docs-governance 生成项目文档」同等深度与完整度。
---

# 文档生成（/doc-generate）

执行**项目文档治理**中的文档生成或补全。必须先读取 Memory ROOT，再执行。**目标**：与用户直接使用「按照 project-docs-governance 生成项目文档」作为提示词时，达到同等的文档数量、章节完整度与交叉引用质量。

**Skill 路径约定**：优先从 `project-docs-governance/` 读取；若不存在则从 `.cursor/skills/project-docs-governance/` 读取（相对于使用方项目仓库根）。

---

## 1. 读取 Memory ROOT

- 优先读取 `.apm/Memory/Memory_Root.md`；若不存在则尝试 `docs/Memory_Root.md` 或询问用户。
- 吸收：项目目标、阶段、技术栈、架构要点、术语、约束，用于生成内容且不与记忆冲突。

---

## 2. 读取本 Skill 与文档体系

- 读取 `project-docs-governance/SKILL.md`（若不存在则 `.cursor/skills/project-docs-governance/SKILL.md`）。
- 读取 `project-docs-governance/references/document-map.md`（文档类型、依赖关系、推荐路径）。
- 若将执行**完整生成**（见下），另读 `project-docs-governance/references/document-practices-summary.md`（若有），以获取各文档类型的必备章节与质量标准。

---

## 3. 确定生成范围（关键：未指定 ≠ 只生成一篇）

### 3.1 用户已指定文档类型或名称

- 若用户明确指定（如「只生成 README」「补全部署手册」「生成 ADR-002」），**仅处理该项**。
- 读取对应的 `project-docs-governance/references/*-guide.md` 与 `project-docs-governance/templates/*.md`，按必备章节与深度生成或增量补全。

### 3.2 用户未指定（默认：完整生成）

- **必须执行「按缺口与依赖顺序生成全部缺失/待补充文档」**，而不是只生成一篇。
- **步骤**：
  1. **盘点**：扫描 `docs/`、仓库根、`.apm/`，若有 `docs/INDEX.md` 则据此识别已存在与标为「待补充」的文档。
  2. **缺口**：对照 document-map 与项目类型（常规 / 含 AI），列出缺失、仅占位或明显过旧的文档。
  3. **按依赖顺序生成**：按下列推荐顺序依次处理（缺失则生成，已存在则增量补全缺失章节、修正过时与术语）：
     - 第一轮（无上游）：项目概述、文档索引(INDEX)、术语表
     - 第二轮：技术选型、环境说明、配置说明
     - 第三轮：系统架构、部署手册（若缺失或过简）
     - 第四轮：运维手册、验收标准、测试计划、安全设计
     - 第五轮：Onboarding、FAQ、监控与告警、Runbook 索引、Release Notes 目录、ADR（至少一则或索引）
  4. **更新文档索引**：在 `docs/INDEX.md` 中更新已生成文档的状态与按角色索引，并追加变更记录。
- **每类文档**：生成时读取对应的 `*-guide.md` 与 `templates/*.md`（若存在），满足必备章节、目标读者、禁忌；与 Memory ROOT、术语表一致；文末含版本、状态、相关文档、变更记录。

---

## 4. 生成与补全规则（统一适用）

- **增量优先**：若目标路径已有文件，在原有结构上补全缺失章节、修正过时处、统一术语，不整篇覆盖除非用户明确要求重写。
- **事实优先**：以 Memory ROOT、现有代码/配置、API 定义为依据；无法确认处标记「待补充」或「待与项目方确认」，不编造。
- **深度与读者**：按对应 guide 的必备/可选章节、目标读者执行；**完整生成时不要省略章节或写「略」**，与「按 project-docs-governance 生成项目文档」提示词下的产出深度一致。
- **对外/对内**：按 guide 区分；术语与 [术语表](glossary.md) 一致。

---

## 5. 输出

- 列出**所有**生成/更新的**文件路径**及每份的**简短变更说明**（新建 / 补全章节 / 修正过时）。
- 若有待补充项（如某节标为「待补充」），在输出中简要列出。
- 全部输出使用中文。
