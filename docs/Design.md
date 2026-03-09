## 0. 思考链（sequential-thinking）
- 目标聚焦：输入 NotebookLM PDF/图片，输出「干净背景 + 可编辑文字」的 PPTX。
- 约束确认：纯前端单页（index*.html），无后端；依赖 pdf.js、PptxGenJS、Gemini 去字与 OCR；需遵守 15 RPM / 1500 RPD 配额与版权检测。
- 设计重点：数据流与尺寸映射、并发与限流、错误/重试、Lite vs Standard 模式提示、导出精准度。
- 结果导向：提供一条清晰流水线（上传→选页→AI→合成→导出），确保高还原度与可编辑性。

## 1. 目标与成功准则
- 目标：尽量还原 NotebookLM 版式，生成可编辑 PPTX，支持速度/配额优先（Lite）或样式优先（Standard）。
- 成功准则：文字框覆盖率 ≥ 95%（Standard），背景残留文字 < 5%，单页耗时 ≤ 5 秒；错误可重试，提示清晰。

## 2. 技术与产品边界
- 前端单页应用；不做服务器存储/运算。
- 依赖：pdf.js 3.11.174（PDF 渲染），PptxGenJS 3.12.0（PPTX），Gemini 2.5 Flash Image（去字），Gemini 2.5 Flash Lite/Standard（OCR）。
- 浏览器：桌面 Chrome/Edge；移动端需保持基本可用（上传、进度、导出）。

## 3. 数据流与管线
1) 上传与渲染  
   - PDF：pdf.js 渲染 2.0x 图像供 AI；生成 0.5x 缩略图供选页。  
   - 图片：FileReader + Canvas 读取，生成 2.0x AI 输入与 0.5x 缩略图。  
   - 产出：页面列表 {id, thumb, fullImage, width, height}。
2) 配置与选页  
   - 用户勾选页面、选择比例（16:9 / 9:16 / 4:3）、选择 OCR 模式（Lite/Standard），输入 API Key（localStorage 保存）。
3) AI 处理（每页）  
   - 并行子任务：去字背景（Gemini Image）+ OCR（Gemini Text），Promise.all。  
   - 并发控制：全局并发数 2-3；对 429/5xx 指数回退重试（最多 3 次）；遵守 15 RPM/1500 RPD。  
   - 失败分类：IMAGE_RECITATION/版权直接失败提示；Key 无效、配额、网络可重试。
4) 合成与导出  
   - 尺寸映射：以 AI 输入图尺寸为基准，映射到 PPT 宽高，保证文字框位置比例一致。  
   - PptxGenJS：背景层用去字图；文字层用 OCR 结果（x/y/width/height、fontSize、bold、color）。Standard 还原样式；Lite 用默认样式。  
   - 导出：生成 PPTX Blob 并下载，附处理摘要（成功/失败页）。

## 4. 模块设计
- UI/状态管理  
  - 状态：文件/页面列表、处理状态（排队/处理中/成功/失败）、进度、选项（比例、模式）、API Key。  
  - 组件：上传区、API Key 区、模式切换、缩略图网格、进度/结果卡片、重试与重置（软重置保留 Key）。
- 解析层  
  - PDF 渲染：pdf.js page.render 输出 Canvas → toDataURL(2.0x)；缩略图 0.5x。  
  - 图片读取：FileReader → Canvas → dataURL。
- AI 封装  
  - requestGemini({type, model, payload}) 内置节流与重试，统一错误码处理。  
  - 去字 Prompt：要求“移除所有文字并修复背景”；对版权提示直接抛错。  
  - OCR：Lite 返回文字与坐标，Standard 追加字号/粗细/颜色，尽可能保留行距/对齐信息。
- 导出层  
  - slideSize 根据用户比例设置；背景添加单张图片；文字框按比例缩放位置与尺寸。  
  - 默认样式（Lite）：中性字体、适中字号/颜色；Standard 使用模型返回样式。

## 5. 错误处理与降级
- 分类提示：Key 无效、配额/429、版权限制、网络/超时。  
- 策略：单页失败不阻塞；允许单页重试；对 429/5xx 重试；对版权错误要求更换素材。  
- 观测：UI 显示耗时、重试次数、成功/失败页数。

## 6. 安全与隐私
- API Key 仅存 localStorage/内存，不传第三方。  
- 图片仅发送至 Gemini 官方 API，不落盘。  
- 提示用户素材可能受版权限制。

## 7. 性能与质量
- 性能：单页 2-5 秒；并发 2-3；必要时节流 1000-1500ms。  
- 质量：文字框覆盖率 ≥ 95%（Standard）；位置偏移 ≤ 3%；背景残留 < 5%；Lite 明确样式缺失。  
- 兼容：桌面优先，移动端保持基本功能。

## 8. 验收与测试
- 用例：NotebookLM PDF（中英混排、大/小标题、列表）、截图、多页长文。  
- 检查：背景残留、文字框偏移、字号层级（Standard）、Lite 是否可编辑。  
- 压力：20+ 页连续处理，验证限流与重试。

## 9. 后续迭代
- 动态并发调整（基于最近延迟）。  
- 手动标注/调整文字框后再导出。  
- 模板化导出（品牌配色/字体预设）。
