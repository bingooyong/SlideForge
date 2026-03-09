# 前端代码规范（React + TypeScript）

本规范适用于本仓库 Web 前端（React + Vite + Zustand），以保持结构清晰、可维护和可扩展。

## 权威参考

- **React + TypeScript Style Guide**：<https://react-typescript-style-guide.com/>

---

## 1. 原则

- **可读与可预测**：结构、命名、放置位置一致，减少认知负担。
- **清晰优于灵活**：优先统一写法，避免为“少写几行”引入难懂模式。
- **封装**：按功能/页面组织，相关组件、hooks、工具放在同一功能目录下。
- **避免过度抽象**：不提前做不必要的封装与泛型。
- **早返回**：用 early return 减少嵌套，提升可读性。
- **关注点分离**：业务逻辑放在 hooks/工具中，组件侧重 UI 与状态绑定。

---

## 2. 目录结构（功能优先）

- **按功能/页面分目录**，例如：`pages/upload/`、`pages/editor/`、`features/task-status/`。
- 功能内可包含：`components/`、`hooks/`、`utils/`、`types.ts`、`constants.ts`。
- **公共部分**：`common/components/`、`common/hooks/`、`common/utils/`；跨功能常量放 `constants/`。
- **配置与集成**：Apollo、Analytics 等放在 `config/` 或等价目录。
- 使用 **index.ts** 做桶文件导出时，以功能为粒度，避免大范围 re-export 导致 tree-shaking 变差；**避免** `import * as X`。

示例（概念结构）：

```
src/
├── common/
│   ├── components/
│   ├── hooks/
│   └── utils/
├── features/
│   ├── upload/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── index.ts
│   └── task-status/
├── pages/
│   └── ...
├── config/
└── constants/
```

---

## 3. 组件结构

- **组件顺序**（自上而下）：Hooks → 派生变量 → `useEffect` → 事件/工具函数 → return (JSX)。
- **命名**：组件文件与文件夹一致（如 `ProfileHero.tsx` 放在 `ProfileHero/` 下）。
- **函数组件**：默认使用函数组件 + Hooks；props/state/context 用 TypeScript 显式类型。
- **children**：使用 `React.ReactNode` 等明确类型，避免 `any`。
- **单一职责**：数据请求、业务逻辑尽量放在自定义 hook 中，组件负责展示与用户交互。

---

## 4. 类型与接口

- 优先 **接口/类型** 明确定义 props、API 响应、全局状态形状。
- 能由类型推断的不必重复写类型；在复杂或公共 API 处使用显式类型。
- 避免 `any`；必要时用 `unknown` 并做类型收窄。
- 使用 **命名导出**，便于重构与 tree-shaking。

---

## 5. 本项目约定

- **栈**：React 18+，TypeScript，Vite，Zustand。
- **风格**：ESLint + Prettier，与仓库根配置一致。
- **API 与 Schema**：与后端约定的请求/响应、WebSocket 消息结构保持一致；类型定义可与共享 Schema 或 OpenAPI 生成对齐。
