import { useState } from "react";

const LINKS = {
  watermark: "https://www.notebooklmwatermark.com/",
  shrink: "https://shrinkpdf.com/",
  cloudConsole: "https://console.cloud.google.com/projectcreate",
  aiStudio: "https://aistudio.google.com/apikey",
};

export function HomeGuidance() {
  const [alertOpen, setAlertOpen] = useState(false);
  const [apiKeyGuideOpen, setApiKeyGuideOpen] = useState(false);
  const [toolsOpen, setToolsOpen] = useState(false);

  return (
    <section className="home-guidance" aria-label="使用说明与版本信息">
      <div className="home-guidance__version">
        <span className="home-guidance__version-badge">v2.3-dual-mode</span>
        <span className="home-guidance__version-desc">
          OCR 双模式：Lite（快速省额度）/ 标准（完整样式）
        </span>
      </div>

      <div className="home-guidance__alert">
        <button
          type="button"
          className="home-guidance__alert-header"
          onClick={() => setAlertOpen((o) => !o)}
          aria-expanded={alertOpen}
        >
          <span className="home-guidance__alert-icon">⚡</span>
          <div className="home-guidance__alert-title-wrap">
            <strong>双模式版本：OCR 模型可选择（Lite 快速省额度 / 标准完整样式）</strong>
            <span className="home-guidance__alert-sub">
              在转换时可选择 OCR 模式，根据需求平衡速度与品质 — 点击展开详情
            </span>
          </div>
          <span className={`home-guidance__chevron${alertOpen ? " home-guidance__chevron--open" : ""}`} aria-hidden>▼</span>
        </button>
        <div className={`home-guidance__alert-body${alertOpen ? " home-guidance__alert-body--open" : ""}`}>
          <ul className="home-guidance__list">
            <li>
              <strong>版本特色：</strong>
              本版本支持 <code>gemini-2.5-flash-lite</code> 进行 OCR，在保持内容准确的同时可节省 API 额度。
            </li>
            <li>
              <strong>模式说明：</strong>
              Lite：文字内容与位置准确，无字体样式检测；标准：完整样式检测，适合需保留视觉层次的简报。
            </li>
            <li>
              <strong>✅ Lite 适用：</strong>
              纯文字笔记、会议记录、内容草稿。
            </li>
            <li>
              <strong>⚠️ Lite 限制：</strong>
              不检测字体大小、粗体、颜色，导出 PPTX 文字为统一样式。
            </li>
            <li>
              <strong>📋 建议：</strong>
              需要完整样式时请选择「Standard（完整样式）」。
            </li>
          </ul>
        </div>
      </div>

      <div className="home-guidance__apikey-wrap">
        <button
          type="button"
          className="home-guidance__tools-trigger"
          onClick={() => setApiKeyGuideOpen((o) => !o)}
          aria-expanded={apiKeyGuideOpen}
        >
          <span className={`home-guidance__chevron${apiKeyGuideOpen ? " home-guidance__chevron--open" : ""}`} aria-hidden>▼</span>
          如何配置免费的 AI Studio API Key（先创建项目，再创建 Key）
        </button>
        <div className={`home-guidance__tools-body${apiKeyGuideOpen ? " home-guidance__tools-body--open" : ""}`}>
          <div className="home-guidance__apikey-body">
            <div className="home-guidance__apikey-block home-guidance__apikey-block--steps">
              <p className="home-guidance__apikey-title">如何取得 API Key</p>
              <ol className="home-guidance__steps">
                <li>
                  前往{" "}
                  <a href={LINKS.cloudConsole} target="_blank" rel="noopener noreferrer">
                    Google Cloud Console
                  </a>{" "}
                  <strong>先建立新专案</strong>（自订名称，例如 "my-notebook-pptx"）。
                </li>
                <li>
                  前往{" "}
                  <a href={LINKS.aiStudio} target="_blank" rel="noopener noreferrer">
                    Google AI Studio
                  </a>
                  。
                </li>
                <li>
                  点击「Create API Key」，<strong>选择你刚建立的那个专案</strong>。
                </li>
                <li>复制产生的 API Key（以 AIza 开头），在本站上传页的「Gemini API Key」栏填入即可（仅本地环境会使用，不会上传到服务器）。</li>
              </ol>
            </div>
            <div className="home-guidance__apikey-block home-guidance__apikey-block--warn">
              <p className="home-guidance__apikey-title">免费方案配额</p>
              <p>免费 API 约 20 次请求/天，每张图片约 2 次请求，每日约可处理 10 张图片；付费方案无此限制。</p>
            </div>
            <div className="home-guidance__apikey-block home-guidance__apikey-block--bug">
              <p className="home-guidance__apikey-title">避开 gen-lang-client Bug</p>
              <p>
                若专案名称包含 <code>gen-lang-client</code>，可能因已知 Bug 无法使用。请务必在 Cloud Console 建立<strong>自订名称的新专案</strong>，再于该专案下在 AI Studio 中创建 API Key。
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="home-guidance__tools-wrap">
        <button
          type="button"
          className="home-guidance__tools-trigger"
          onClick={() => setToolsOpen((o) => !o)}
          aria-expanded={toolsOpen}
        >
          <span className={`home-guidance__chevron${toolsOpen ? " home-guidance__chevron--open" : ""}`} aria-hidden>▼</span>
          PDF 前处理工具（选用）
        </button>
        <div className={`home-guidance__tools-body${toolsOpen ? " home-guidance__tools-body--open" : ""}`}>
          <div className="home-guidance__tool-grid">
            <a
              href={LINKS.watermark}
              target="_blank"
              rel="noopener noreferrer"
              className="home-guidance__tool-card"
            >
              <span className="home-guidance__tool-title">移除浮水印</span>
              <span className="home-guidance__tool-desc">移除 NotebookLM 浮水印，提升处理效果</span>
              <span className="home-guidance__tool-ext" aria-hidden>↗</span>
            </a>
            <a
              href={LINKS.shrink}
              target="_blank"
              rel="noopener noreferrer"
              className="home-guidance__tool-card"
            >
              <span className="home-guidance__tool-title">压缩 PDF</span>
              <span className="home-guidance__tool-desc">减少档案大小，加快上传与处理速度</span>
              <span className="home-guidance__tool-ext" aria-hidden>↗</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
