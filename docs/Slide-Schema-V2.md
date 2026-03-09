# Slide Schema V2：容器嵌套与对接说明

## 1. 设计目标

为将幻灯截图**精准还原为排版一致且完全可编辑**的 PPTX，结构化数据需要表达：

- **视觉层级**：页面 → 组合容器（如左右卡片）→ 内部标题/正文/列表
- **容器关系**：子元素 bbox 相对父容器归一化 (0-1)，便于比例保持与坐标换算
- **富文本**：同一段内多样式（粗体+常规、颜色）用 `content`/`text` 数组，对应 `python-pptx` 的 `add_run()`
- **图标+文字混排**：`icon_text_layout` 明确左侧图标占位与右侧文案，便于后端插入裁剪后的 PNG

## 2. 与现有 Pipeline 的关系

| 环节 | 当前 (V1) | V2 可选路径 |
|------|-----------|-------------|
| OCR 输出 | 扁平 `blocks`（TextBlock/ImageBlock） | 大模型输出 `slide_metadata` + `elements` 树形结构 |
| 背景净化 | 用 `TextBlock.box` 建 mask | 用 `collect_text_bboxes_absolute(doc_v2)` 得到绝对 bbox，再通过 `slide_document_v2_to_text_blocks_for_mask(doc)` 转成 `List[TextBlock]` 传入 `clean_background` |
| PPTX 合成 | `create_slide(prs, slide_schema, background, cropped_images, style_info)` | `create_slide_v2(prs, doc_v2, background, icon_images)`，图标由 `placeholder_id` 映射到裁剪图 |

V2 与 V1 **可并存**：根据大模型返回的根键（`blocks` 还是 `elements`）选择解析路径与合成函数。

## 3. 核心模块

- **Schema 与 bbox 收集**：`app.pipeline.slide_schema_v2`
  - `SlideDocumentV2`、`ElementV2`（group / text_block / shape_text_box / icon_text_layout / list_block）
  - `collect_text_bboxes_absolute(doc)`：递归遍历，相对 bbox 转绝对 (0-1)
  - `slide_document_v2_to_text_blocks_for_mask(doc)`：得到 `List[TextBlock]` 供 `clean_background`
- **PPTX 渲染**：`app.pipeline.pptx_composition_v2`
  - `create_slide_v2(prs, doc, background, icon_images)`：先铺背景图，再按 `elements` 递归绘制圆角容器、文本框（富文本）、图标+文字、列表

## 4. 大模型输出约定

- 根结构：`{ "slide_metadata": { ... }, "elements": [ ... ] }`
- 顶层 `elements` 的 bbox 为**相对页面**的归一化 [x, y, w, h]；`group` 内子元素 bbox 为**相对该 group** 的归一化。
- 需从背景上去除的区域（正文、水印、覆盖字等）都应落在某类带 bbox 的节点中，以便 `collect_text_bboxes_absolute` 收集后做 mask。

## 5. 如何验证

在 **backend** 目录下执行：

```bash
# 使用内置 V2 示例数据，生成纯色背景的 PPTX（不依赖图片）
python scripts/verify_schema_v2.py

# 使用指定图片做背景（会先做背景净化，用 V2 的 bbox 做文字蒙版）
python scripts/verify_schema_v2.py --image ../assets/demo-001.jpg

# 指定输出路径
python scripts/verify_schema_v2.py -o my_v2.pptx
```

脚本会：解析 V2 文档 → 调用 `collect_text_bboxes_absolute` 与 `slide_document_v2_to_text_blocks_for_mask` → 生成 PPTX（可选带净化背景）。输出文件默认名为 `verify_schema_v2_out.pptx`，用 PowerPoint 或 WPS 打开即可检查版式、圆角、红框、列表等是否按 Schema V2 正确渲染。

## 6. 破局：Few-Shot + 结构化输出

为避免大模型退化成「只做 OCR、不输出 group/富文本」的扁平结构，采用两种约束并用：

- **策略一：Few-Shot 提示词**  
  `_build_prompt_v2()` 内已内置一份**必须模仿**的 JSON 示例：页面标题 `text_block`、左右两个白底卡片 `group`（含 `background_shape`）、蓝条 `shape_text_box`、带图标的 `icon_text_layout`（`text` 为多 run 数组）、红框嵌套 `group` 与 `list_block`。大模型会依此输出嵌套与富文本结构。

- **策略二：Gemini 结构化输出（Structured Output）**  
  当 `analyze_layout_v2(..., use_structured_output=True)` 且后端为 Gemini 时，在请求中传入 `generation_config.response_mime_type="application/json"` 与 `generation_config.response_schema=SlideDocumentV2.model_json_schema()`，强制 API 返回符合 Schema 的 JSON（含 `elements`、`group`、`children` 等）。若当前环境或模型不支持 schema，会自动回退为仅 Few-Shot 调用。  
  配置项：`LAYOUT_OCR_V2_STRUCTURED_OUTPUT`（默认 `true`）；设为 `false` 可关闭 schema，仅用 Few-Shot。

## 7. LLM 提示词与渲染约定

- **V2 系统提示词**：`gemini_layout_ocr._build_prompt_v2()` 提供优化后的系统提示词，要求大模型输出「容器嵌套 + 相对坐标」、子元素 bbox 相对父容器、内边距、富文本分段、`icon_text_layout`/`list_block` 等。通过 `analyze_layout_v2(page_image)` 调用 Gemini/GLM 并解析为 `SlideDocumentV2`。
- **渲染端约定**：
  - 仅当 JSON 中 `shadow: true` 时保留形状阴影，否则关闭默认阴影（`shape.shadow.inherit = False`）。
  - 文本框统一 `word_wrap = True`，且将 `margin_left/right/top/bottom` 设为 0，减少蓝色标题栏等文字溢出。
  - 子元素坐标换算：`left_inch = parent_x + child_bbox[0] * parent_width`（及 y/width/height 同理），在 `_render_element` 中已按此实现。

## 8. 后续可做

- Pipeline 中根据配置或 LLM 返回格式选择 `analyze_layout`（V1）或 `analyze_layout_v2`（V2），并选择 `create_slide` 或 `create_slide_v2`。
- 图标裁剪结果按 `placeholder_id` 填入 `icon_images` 再传入 `create_slide_v2`。
