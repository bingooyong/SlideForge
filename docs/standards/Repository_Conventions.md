# 仓库与协作规范

本规范约定仓库级文件、分支、提交与协作流程，与 GitHub 等平台最佳实践对齐。

## 参考

- GitHub：<https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories>
- 贡献指南：<https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors>

---

## 1. 必备文件

| 文件 | 位置 | 说明 |
|------|------|------|
| **README.md** | 仓库根目录 | 项目简介、用途、如何安装/运行、基本用法、链接到更多文档（如 docs/、API 契约）。 |
| **CONTRIBUTING.md** | 根目录或 `.github/` 或 `docs/` | 如何参与：分支策略、提交规范、如何提 Issue/PR、代码规范索引（可指向 docs/Code_Standards.md）。 |
| **LICENSE** | 根目录 | 明确项目许可证。 |
| **.env.example** | 根目录或后端目录 | 列出所需环境变量（不含敏感值），便于本地与部署配置。 |

可选但推荐：

- **SECURITY.md**：安全相关问题如何报告。
- **.editorconfig**：统一缩进、换行符等，与 Code_Standards 一致。

---

## 2. 文档放置

- **产品/需求/设计**：`docs/`（如 PRD.md、Design.md、PRD-zh.md）。
- **代码与仓库规范**：`docs/Code_Standards.md` 与 `docs/standards/` 下各专项规范。
- **API 契约与 Schema**：可在 `docs/api/` 或与后端 schema 同仓的 `openapi.yaml` 等，并在 README 中说明。

---

## 3. 分支与提交

- **main / master**：默认主分支，保持可部署或可发布状态。
- **功能/修复**：在单独分支开发（如 `feature/xxx`、`fix/xxx`），通过 PR 合并到主分支。
- **提交信息**：
  - 建议使用清晰的一句式摘要；可选前缀（如 `feat:`、`fix:`、`docs:`、`chore:`）便于生成 Changelog。
  - 示例：`feat(api): add task status WebSocket endpoint`、`docs: add Python style guide to docs/standards`。
- 合并前建议通过 CI（lint、测试、类型检查）；大型变更可在 PR 描述中说明设计与影响范围。

---

## 4. Pull Request 与 Code Review

- PR 描述：说明改动目的、相关 Issue（如有）、测试方式或验收要点。
- 遵循 [docs/Code_Standards.md](../Code_Standards.md) 及 `docs/standards/` 下规范；Review 时关注风格、可维护性与契约一致性。
- 合并策略（由维护者决定）：如 squash merge 或 merge commit，在 CONTRIBUTING.md 中写明。

---

## 5. 本项目约定

- **Python**：本地开发与运行须使用 **venv** 虚拟环境（见 CONTRIBUTING.md）；不在系统 Python 下直接安装项目依赖。
- 规范以 `docs/` 与 `docs/standards/` 为准；新成员参与前阅读 README、CONTRIBUTING 与 Code_Standards。
- 提交前本地运行格式化与 lint（Black/ESLint 等），与 CI 配置一致。
- 涉及 API 或共享 Schema 的变更，需同步更新契约文档或 OpenAPI，并在 PR 中注明。
