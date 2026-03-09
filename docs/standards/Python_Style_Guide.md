# Python 代码规范（服务端）

本规范以 **PEP 8** 与 **Google Python Style Guide** 为基准，适用于本仓库所有服务端 Python 代码（FastAPI、流水线、工具脚本等）。

## 权威参考

- **PEP 8**（官方）：<https://peps.python.org/pep-0008/>
- **Google Python Style Guide**：<https://google.github.io/styleguide/pyguide.html>
- 推荐使用 **Black** 或 **Pyink** 做自动格式化，减少风格争论。

---

## 1. 语言与 Lint

- **类型注解**：新代码应使用类型注解（function/return、变量在必要时）。支持 `str | None`、`list[int]` 等现代语法。
- **Lint**：使用 `pylint` 或 `ruff` 做静态检查。若需抑制某条告警，使用行内注释并说明原因，例如：`# pylint: disable=invalid-name`。
- **导入**：仅对包/模块使用 `import`，使用完整包路径，避免相对导入（同一包内也建议用完整包名）。可为长名称使用 `from x import y as z`。

---

## 2. 命名

- **模块/包**：`lower_with_under`。
- **类**：`CapWords`。
- **函数/方法/变量**：`lower_with_under`。
- **常量**：`UPPER_WITH_UNDER`。
- **“内部”符号**：单下划线前缀 `_internal_name`。
- 避免单字符名（除循环变量、坐标 x/y 等）；避免与内置/类型名冲突。

---

## 3. 格式

- **缩进**：4 空格，不用 Tab。
- **行宽**：建议 ≤88 字符（Black 默认）；长表达式可换行，优先在括号/逗号后断行。
- **空行**：顶层定义之间两行；类内方法之间一行。
- **尾逗号**：多行序列末尾可保留尾逗号，便于 diff 与 Black 格式化。

---

## 4. 文档与注释

- **Docstring**：公开模块、类、函数/方法应有 docstring；格式可采用 Google 风格（Summary、Args、Returns、Raises）。
- **注释**：用英文或与项目一致；解释“为什么”而非“做什么”；过时逻辑删除而非仅注释掉。
- **TODO**：使用 `# TODO(author): 说明` 便于追踪。

---

## 5. 异常与错误处理

- 优先使用内置异常类型（如 `ValueError`、`TypeError`）。
- 不用 `assert` 做业务逻辑或参数校验（仅用于“不应发生”的检查）；测试中可用 `assert`。
- 避免裸 `except:`；尽量只捕获具体异常；`try` 块保持短小；需要清理时使用 `finally`。
- 自定义异常以 `Error` 结尾，继承自 `Exception` 等标准类型。

---

## 6. 其他要点

- **可变默认参数**：禁止 `def f(x, lst=[])`，使用 `None` 并在函数内初始化。
- **全局可变状态**：避免；若必须使用，用 `_` 前缀并文档说明。
- **推导式**：允许列表/字典/集合推导与生成器表达式，但复杂逻辑优先可读性，避免多重 `for`/复杂过滤挤在一行。
- **Lambda**：仅用于简单单表达式；更复杂逻辑用普通函数。

---

## 7. 本项目约定

- Python 版本：**3.11+**。
- 格式化：**Black**（或 Pyink），配置与 CI 一致。
- 类型检查：可选 **pyright** 或 **mypy**；若启用，在 CI 中统一运行。
- 服务端入口与路由结构见 [Backend_Structure.md](Backend_Structure.md)。
