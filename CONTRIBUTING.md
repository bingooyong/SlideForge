# 参与贡献

感谢你考虑为 SlideForge 做贡献。请先阅读本仓库的代码与协作规范，再提交 Issue 或 Pull Request。

> 本项目灵感/参考自 [laihenyi/NBLM2PPTX](https://github.com/laihenyi/NBLM2PPTX)。

## 规范与约定

- **代码与仓库规范总览**：[docs/Code_Standards.md](docs/Code_Standards.md)  
  包含 Python、React/TypeScript、FastAPI 结构、仓库约定等索引。
- **仓库与协作细则**：[docs/standards/Repository_Conventions.md](docs/standards/Repository_Conventions.md)  
  分支、提交信息、PR 与 Code Review 约定。

## 开发前

1. Fork 本仓库并在本地克隆。
2. **Python 开发**：请使用 **venv** 虚拟环境，不要用系统 Python 直接安装依赖。
   - 在仓库根目录创建并激活：
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate   # Linux/macOS
     # Windows: .venv\Scripts\activate
     ```
   - 安装后端依赖：`pip install -r backend/requirements.txt`
   - 运行/调试后端时保持该 venv 激活。
3. 安装依赖并确保本地通过 lint/格式化（见各子项目 README 或根目录说明）。
4. 新功能或修复请在单独分支上进行（如 `feature/xxx`、`fix/xxx`），通过 Pull Request 合并到主分支。

## 提交与 PR

- 提交信息请清晰描述改动；可选使用 `feat:`、`fix:`、`docs:` 等前缀。
- PR 描述中请说明改动目的与验收方式；涉及 API 或共享 Schema 时请同步更新相关文档。

如有疑问，可在 Issue 中提出。
