# 智谱 GLM 账号模型限制

本页记录当前账号在智谱开放平台（open.bigmodel.cn）的**模型并发限制**，用于配置本项目的 `LAYOUT_OCR_PROVIDER=glm` 时选用合适模型与 `GLM_MAX_RPM`。

> 说明：本页面模型并发仅适用于「余额消耗」的 API 用户；**GLM Coding 套餐**用户请以套餐权益为准。

---

## 当前速率限制（并发数）

API 使用受**并发数**（在途请求任务数量）限制。限制量级与用户权益等级相关，详见 [用户权益](https://docs.bigmodel.cn/cn/guide/platform/equity-explain)。

| 模型类型       | 模型名称                     | 并发数 |
| -------------- | ---------------------------- | ------ |
| 通用模型       | GLM-4.6                      | 3      |
| 通用模型       | GLM-4.6V-FlashX              | 3      |
| 通用模型       | GLM-4.7                      | 3      |
| 图像大模型     | GLM-Image                    | 1      |
| 通用模型       | GLM-Z1-Air                   | 30     |
| 通用模型       | GLM-4.5                      | 10     |
| 向量模型       | embedding-3-pro              | 100    |
| 通用模型       | GLM-4.6V                     | 10     |
| 通用模型       | GLM-4.7-Flash                | 1      |
| 通用模型       | GLM-4.7-FlashX               | 3      |
| 通用模型       | GLM-OCR                      | 2      |
| 通用模型       | GLM-5                        | 5      |
| 通用模型       | GLM-4-Plus                   | 20     |
| 通用模型       | GLM-Z1-Flash                 | 30     |
| 通用模型       | GLM-Z1-AirX                  | 30     |
| 通用模型       | GLM-4.5V                     | 10     |
| 通用模型       | GLM-4.6V-Flash               | 1      |
| 通用模型       | AutoGLM-Phone                | 5      |
| 通用模型       | AutoGLM-Phone-Multilingual   | 5      |
| 通用模型       | GLM-4-0520                   | 20     |
| 通用模型       | Search-Pro                   | 5      |
| 通用模型       | Search-Std                  | 50     |
| 通用模型       | GLM-4.5-Air                  | 5      |
| 通用模型       | GLM-4.5-AirX                 | 5      |
| 通用模型       | GLM-4-AirX                   | 5      |
| 实时音视频模型 | GLM-Realtime                 | 5      |
| 通用模型       | GLM-4-Flash-250414           | 5      |
| 通用模型       | GLM-4-FlashX-250414          | 50     |
| 实时音视频模型 | GLM-Realtime-Flash           | 5      |
| 实时音视频模型 | GLM-Realtime-Air             | 5      |
| 通用模型       | GLM-4.5-Flash                | 2      |
| 通用模型       | GLM-4V-Plus-0111             | 5      |
| 通用模型       | GLM-Zero-Preview             | 50     |
| 通用模型       | GLM-4-Air                    | 100    |
| 通用模型       | GLM-4-Air-250414             | 30     |
| 通用模型       | GLM-4-32B-0414-128K          | 15     |
| 通用模型       | GLM-4-Long                   | 10     |
| 通用模型       | GLM-4-FlashX                 | 50     |
| 通用模型       | GLM-4.1V-Thinking-Flash      | 5      |
| 通用模型       | GLM-4.1V-Thinking-FlashX     | 30     |
| 通用模型       | GLM-4-Voice                  | 5      |
| 通用模型       | GLM-4-Flash                  | 200    |
| 通用模型       | GLM-Z1-FlashX                | 50     |
| 通用模型       | GLM-4-9B                     | 5      |
| 通用模型       | GLM-4V-Plus                  | 5      |
| 通用模型       | GLM-4V-Flash                 | 10     |
| 通用模型       | GLM-4V                       | 5      |
| 通用模型       | Web-Search-Pro               | 30     |
| 实时音视频模型 | GLM-ASR                      | 5      |
| 重排序模型     | Rerank                       | 50     |
| 图像大模型     | CogView-4-250304             | 5      |
| 图像大模型     | CogView-3-Plus               | 5      |
| 图像大模型     | CogView-4                    | 5      |
| 图像大模型     | CogView-3-Flash              | 5      |
| 图像大模型     | CogView-3                    | 5      |
| 视频生成模型   | CogVideoX-Flash              | 3      |
| 视频生成模型   | CogVideoX                    | 5      |
| 视频生成模型   | CogVideoX-2                  | 5      |
| 音频模型       | CogTTS-Clone                 | 2      |
| 实时音视频模型 | CogTTS                       | 5      |
| 实时音视频模型 | GLM-TTS                      | 5      |
| 音频模型       | GLM-TTS-Clone                | 2      |
| 实时音视频模型 | GLM-ASR-2512                 | 5      |
| 视频生成模型   | ViduQ1-text                  | 5      |
| 视频生成模型   | Viduq1-Image                 | 5      |
| 视频生成模型   | Viduq1-Start-End             | 5      |
| 视频生成模型   | Vidu2-Image                  | 5      |
| 视频生成模型   | Vidu2-Start-End              | 5      |
| 视频生成模型   | Vidu2-Reference               | 5      |
| 向量模型       | Embedding-3                  | 50     |
| 向量模型       | Embedding-2                  | 50     |
| 通用模型       | GLM-4-AllTools               | 5      |
| 通用模型       | GLM-4-Assistant              | 5      |
| 代码模型       | CodeGeeX-4                   | 50     |
| 通用模型       | GLM-4                        | 30     |
| 通用模型       | CharGLM-4                    | 5      |
| 通用模型       | GLM-3-Turbo                  | 50     |
| 模型工具       | Moderation                   | 5      |
| 视频生成模型   | CogVideoX-3                  | 1      |
| 通用模型       | GLM-Experimental-Preview     | 5      |

---

## 本项目版面 OCR 可用的视觉模型

版面 OCR 需要**视觉模型**（能看图并输出 JSON）。根据上表，可选模型及建议配置如下（`GLM_MAX_RPM` 建议 ≤ 该模型并发数，本项目按「每分钟请求数」做限流）：

| 模型名称（GLM_LAYOUT_MODEL） | 并发数 | 说明 |
| ---------------------------- | ------ | ---- |
| GLM-4.6V                     | 10     | 旗舰视觉，适合版面解析 |
| GLM-4.6V-Flash               | 1      | 轻量，并发低 |
| GLM-4.6V-FlashX              | 3      | 轻量高速 |
| GLM-4.5V                     | 10     | 视觉推理 |
| GLM-4V-Plus / GLM-4V-Plus-0111 | 5    | 多模态 |
| GLM-4V-Flash                 | 10     | 视觉，并发尚可 |
| GLM-4V                       | 5      | 视觉 |
| GLM-4.1V-Thinking-Flash      | 5      | 视觉+思考 |
| GLM-4.1V-Thinking-FlashX     | 30     | 视觉+思考，并发高 |
| GLM-OCR                      | 2      | 专用 OCR，并发较低 |

**.env 示例（按你账号限制设置）：**

```bash
LAYOUT_OCR_PROVIDER=glm
GLM_API_KEY=你的Key
# 选一个上表中你账号可用的视觉模型（注意 API 里可能用小写或带后缀，以文档为准）
GLM_LAYOUT_MODEL=glm-4.6v
# 不超过该模型并发数，例如 10
GLM_MAX_RPM=10
```

---

## GLM Coding 套餐用户（Lite / Pro / Max）

若使用 [GLM Coding Plan](https://docs.bigmodel.cn/cn/coding-plan/overview)（编码套餐），需使用**专属 Coding 端点**，且套餐**并发数较低**，易出现 429 限流。

套餐提供 [视觉理解 MCP Server](https://docs.bigmodel.cn/cn/coding-plan/mcp/vision-mcp-server)，对应旗舰视觉推理模型 **GLM-4.6V**（理解 UI 图、流程图、截图文字等）。若该能力在 Coding 端点的 chat/completions 中开放，可优先用 **glm-4.6v** 做版面 OCR。

**推荐 .env：**

```bash
LAYOUT_OCR_PROVIDER=glm
GLM_API_KEY=你的Coding套餐Key
GLM_API_BASE=https://open.bigmodel.cn/api/coding/paas/v4
# 并发很紧，务必设为 1，避免 429
GLM_MAX_RPM=1
# 套餐视觉能力对应 GLM-4.6V，先试 glm-4.6v；若 429 再试 glm-4v-plus（或改用通用端点+余额）
GLM_LAYOUT_MODEL=glm-4.6v
```

- 先运行 `python scripts/test_glm_connectivity.py`，确认 glm-4.6v 在 Coding 端点可用后再跑版面 OCR。
- 若 glm-4.6v / glm-4v-plus 均返回 429「余额不足」：表示视觉模型不占套餐额度，需用通用端点 `https://open.bigmodel.cn/api/paas/v4` 并充值，或改用 Gemini 做版面 OCR。
- 套餐额度为「每 5 小时 / 每周」限额，单独调用 API 的计费与额度以官方说明为准。

---

## V2 版面解析（容器嵌套 + 相对坐标）

GLM 端**无**类似 Gemini 的 `response_schema` 强约束，且**不擅长**在提示词约束下做“相对坐标”的数学计算，因此采用「Prompt 放宽、Normalizer 算数学」的策略：

- **提示词**（`build_prompt_v2_glm`）：
  - **允许** bbox 使用**全局绝对比例坐标** `[x, y, width, height]`（0～1），不强制相对父容器，避免 GLM 算错；
  - 强约束节点类型：`text_box` / `shape_text_box` / `icon_text_layout` / `group`，禁止自创 `list_item` 等；
  - 要求 `slide_data.elements` 结构、`font_size` 为相对幻灯片高度比例。
- **清洗**（`normalize_glm_v2_output`）：
  - 将疑似 `[x1, y1, x2, y2]` 的 bbox 转为 `[x, y, width, height]`；
  - `page` → `slide_data`，扁平化 `style`，`list_item` → `text_box`；
  - **关键**：递归将子元素的**全局绝对坐标**换算为**相对父容器的坐标**，供 `pptx_composition_v2` 正确渲染嵌套。

追求**极致稳定性**时建议用 Gemini + `response_schema`；必须用国内模型时，上述「允许绝对坐标 + Normalizer 换算」可避免渲染时内容挤在左上角或错位。

---

## 速率限制说明

- 为确保 GLM-4-Flash 在免费调用期间的服务稳定性，当请求上下文超过 8K 时，系统将限制并发为标准速率的 1%。
- 当前账号：**用户权益 V0 并发保障权益**，详见 [用户权益](https://docs.bigmodel.cn/cn/guide/platform/equity-explain)。
