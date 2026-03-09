## 0. 思考鏈（sequential-thinking）
- 目標收斂：把 NotebookLM 輸出的 PDF/圖片轉成「背景圖 + 可編輯文字」的 PPTX。
- 已有能力：前端單頁（index*.html），pdf.js 解析、Gemini 去字+OCR、PptxGenJS 導出、多語言版本、Lite/Standard 模式。
- 缺口：缺少正式需求文檔以對齊邊界、質量標準與驗收。
- 方針：純前端、零部署，明確流程（上傳→選頁→AI→合成→匯出）、併發限流、錯誤重試、質量度量。

## 1. 背景與目標
- NotebookLM PDF 多為圖片內嵌文字，難以編輯與復用。
- 產品目標：提供瀏覽器端轉換工具，分離背景與文字層，輸出可編輯的 PPTX，保持版面還原度，支持多語言 UI。
- 結果形態：單頁 Web 應用；無伺服器端存儲/運算；僅調用 Gemini API。

## 2. 使用者與場景
- 角色：講師/培訓、售前/產品、運營/市場、內容創作者。
- 場景：拿到 NotebookLM PDF 或截圖，需快速轉為 PPT，保留版面並可改字改樣式；需要在速度與樣式還原之間自行取捨。

## 3. 範圍
- 上傳：PDF（用 pdf.js 解析）、圖片（JPG/PNG/WebP/BMP）；支持多文件、多頁；生成縮圖供選頁。
- AI 處理：Gemini 去字背景（2.5 Flash Image），Gemini OCR（2.5 Flash Lite/Standard）；單頁內去字與 OCR 並行，跨頁併發可控。
- 模式：Lite（速度/配額優先，無樣式）、Standard（還原字級/粗細/顏色）。
- 輸出：PptxGenJS 建立背景層+文字層，比例 16:9 / 9:16 / 4:3。
- 體驗：進度/狀態顯示，錯誤提示與單頁重試，軟重置保留 API Key，多語言界面（zh-TW/zh-CN/en/es/ja/fr）。
- 安全：API Key 存 localStorage，不經第三方伺服器；圖片僅送 Gemini API。

## 4. 非範圍
- 伺服器端運算、檔案存儲、權限管理。
- 自動品牌模板套用、動畫生成、審核合規判斷（僅提示 Gemini 版權錯誤）。
- 離線模式與本地安裝包。

## 5. 功能需求
- 上傳/預覽：拖拽或點擊上傳；列出文件名與頁數；縮圖 0.5x 用於選頁；原圖/渲染圖 2.0x 送 AI。
- 選項：選頁、選比例、選模式（Lite/Standard）；API Key 輸入與保存。
- AI 處理：每頁任務 = 去字 + OCR；Promise.all 並行；對 429/5xx 重試（最多 3 次，指數回退）；版權/IMAGE_RECITATION 直接失敗提示。
- 進度與結果：顯示排隊/處理中/成功/失敗；提供單頁重試；展示背景+文字疊加預覽。
- 匯出：生成 PPTX；背景用去字圖；文字框使用 OCR 坐標/字級/粗細/顏色（Standard 有樣式，Lite 用預設樣式）。

## 6. 非功能性需求
- 性能：單頁目標 2-5 秒（含網路）；跨頁併發控制在 2-3 任務；遵守 Gemini 15 RPM / 1500 RPD。
- 兼容：桌面 Chrome/Edge 最新版；行動端保持可上傳、可查看進度與匯出。
- 安全/隱私：API Key 僅本地；圖片不上傳第三方；提示用戶素材授權風險。
- 可維護：依賴版本固定（pdf.js 3.11.174、pptxgenjs 3.12.0）；核心邏輯純前端 JS/HTML。

## 7. 質量與驗收
- 文字覆蓋率：Standard 模式可編輯文字框覆蓋率 ≥ 95%，背景殘留文字 < 5%。
- 位置/樣式：文字框與原文位置偏移可接受 ≤ 3%（寬/高比例）；Standard 保留主副標題字級層級。
- 穩定性：單頁失敗不阻塞整批；重試後成功率 ≥ 90%。
- 驗收素材：NotebookLM PDF（含中英文、大標/小標/列表）、圖片截圖、多頁長文。

## 8. 里程碑
- M1：完成需求/設計文檔並對齊併發與重試策略。
- M2：完善錯誤/配額提示、單頁重試與模式差異提示，多語言同步。
- M3：驗收質量與性能，更新 README/示例資產，發佈穩定版。

## 9. 全栈实现（本仓库）

本仓库为 **FastAPI 后端 + React 前端** 实现，与 §1 中「单页 Web、零部署」的纯前端形态并存为另一交付形态。

- **后端**：FastAPI 提供 `POST /upload`、`GET /tasks/{taskId}`、`GET /export/{taskId}`、WebSocket `/ws/progress`；Pipeline 串联 PDF→页图、Gemini 版面 OCR、配色、裁剪、背景净化、python-pptx 合成；单页失败时降级为原图占位，见 [degradation-strategy.md](degradation-strategy.md)。
- **前端**：React + Vite，上传、实时进度（WebSocket）、导出 PPTX；进度与任务状态与后端契约一致（见 `docs/api/openapi.yaml`）。
- **部署**：本地开发见 README 快速开始；部署步骤见 [Deployment.md](Deployment.md)。
