# 安装与使用（独立仓库维护）

本仓库为**项目文档治理** Skill + 命令一体包，可单独克隆、Fork 或在其他项目中引用。

## 目录结构

```
project-docs-governance/
├── SKILL.md           # 技能主文件
├── INSTALL.md         # 本安装说明
├── DELIVERY.md        # 交付与设计说明
├── agents/
│   └── openai.yaml
├── commands/          # Claude Code / Cursor Slash 命令（7 个）
│   ├── doc-audit.md
│   ├── doc-gap-analysis.md
│   ├── doc-generate.md
│   ├── doc-sync.md
│   ├── doc-update.md
│   ├── doc-release-check.md
│   └── doc-runbook-create.md
├── references/
└── templates/
```

## 在使用方项目中的安装方式

### 方式一：本仓库作为项目子目录（推荐，便于独立 Git 维护）

1. 在使用方项目根目录下放入本仓库：
   - **Git submodule**：`git submodule add <你的 project-docs-governance 仓库 URL> project-docs-governance`
   - 或直接复制/克隆到 `project-docs-governance/`

2. 将命令挂载到 Claude Code / Cursor：
   - **Claude Code**：把 `project-docs-governance/commands/*.md` 复制到使用方项目的 `.claude/commands/`
   - **Cursor**：复制到 `.cursor/commands/`（若使用 Cursor 的 commands 目录）
   - 或在使用方项目中建立符号链接，例如：
     ```bash
     # 在使用方项目根执行
     mkdir -p .claude/commands
     ln -sf ../../project-docs-governance/commands/doc-*.md .claude/commands/
     ```

3. 确保执行命令时，当前工作目录为**使用方项目根**，这样命令内引用的 `project-docs-governance/SKILL.md`、`project-docs-governance/references/` 等路径可正确解析。

### 方式二：Skill 安装到 Cursor 全局，命令仍从本仓库复制

1. 将本仓库复制到 Cursor 技能目录，使 Skill 全局可用：
   - `cp -R project-docs-governance ~/.cursor/skills/project-docs-governance`
   - 或 `~/.cursor/skills/` 下 clone 你的 project-docs-governance 仓库

2. 在使用方项目中只复制命令：
   - 把 `project-docs-governance/commands/*.md` 复制到该项目的 `.claude/commands/`（或 `.cursor/commands/`）
   - 命令会优先找项目根下的 `project-docs-governance/`，找不到再找 `.cursor/skills/project-docs-governance/`，因此全局安装后仍可正常工作。

## 命令与 Skill 路径约定

命令文件内约定的查找顺序（路径均相对于**使用方项目**的仓库根）：

1. `project-docs-governance/SKILL.md`、`project-docs-governance/references/`、`project-docs-governance/templates/`
2. 若不存在，则 `.cursor/skills/project-docs-governance/` 下同名文件

因此：
- 本仓库放在使用方项目的 `project-docs-governance/` 下时，无需再安装到 `.cursor/skills/`。
- 本仓库只安装到 `~/.cursor/skills/project-docs-governance/` 时，仅复制命令到使用方项目的 `.claude/commands/` 即可。

## 可用命令列表

| 命令 | 说明 |
|------|------|
| `/doc-audit` | 文档审计 |
| `/doc-gap-analysis` | 文档缺口分析 |
| `/doc-generate` | 生成/补全指定文档 |
| `/doc-sync` | 文档同步（术语、引用、版本） |
| `/doc-update` | 按变更原因增量更新文档 |
| `/doc-release-check` | 发布前文档检查 |
| `/doc-runbook-create` | 创建单则 Runbook |

执行前会自动读取使用方项目中的 Memory ROOT（默认 `.apm/Memory/Memory_Root.md` 或 `docs/Memory_Root.md`）。

## 独立 GitHub 维护建议

- 将本仓库单独建为 GitHub 仓库（或从当前仓库拆出），仅包含 `project-docs-governance/` 目录内容。
- 其他项目通过 **submodule** 或 **复制 commands + 引用本仓库** 的方式使用，命令与 Skill 均从本仓库取数，便于统一更新。
- 更新命令或 Skill 后，在使用方项目中更新 submodule（`git submodule update --remote project-docs-governance`）或重新复制 `commands/*.md` 即可。
