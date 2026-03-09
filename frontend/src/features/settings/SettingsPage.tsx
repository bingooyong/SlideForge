import { useState, useEffect } from "react";
import { getSettings, saveSettings, AppSettings } from "../../stores/settingsStore";

export function SettingsPage() {
  const [form, setForm] = useState<AppSettings>(getSettings);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setForm(getSettings());
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveSettings(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="settings-page">
      <header className="settings-page__header">
        <h2>模式与配置</h2>
        <p>在此配置 Gemini API Key 与默认转换选项，仅保存在本机浏览器中。</p>
      </header>

      <form className="settings-page__form" onSubmit={handleSubmit}>
        <div className="settings-page__field settings-page__field--full">
          <label htmlFor="settings-gemini-key">Gemini API Key</label>
          <input
            id="settings-gemini-key"
            type="password"
            value={form.geminiApiKey}
            onChange={(e) => setForm((f) => ({ ...f, geminiApiKey: e.target.value }))}
            placeholder="以 AIza 开头；留空则使用服务端 .env 中的 GEMINI_API_KEY"
            autoComplete="off"
          />
          <span className="settings-page__hint">
            上传任务时可使用此处保存的 Key，或在上传页临时覆盖。先创建 Google Cloud 专案，再在 AI Studio 创建 Key。
          </span>
        </div>

        <div className="settings-page__field">
          <label htmlFor="settings-mode">默认转换模式</label>
          <select
            id="settings-mode"
            value={form.defaultMode}
            onChange={(e) => setForm((f) => ({ ...f, defaultMode: e.target.value as "lite" | "standard" }))}
          >
            <option value="lite">Lite（快速，无样式）</option>
            <option value="standard">Standard（完整样式）</option>
          </select>
        </div>

        <div className="settings-page__field">
          <label htmlFor="settings-aspect">默认画面比例</label>
          <select
            id="settings-aspect"
            value={form.defaultAspectRatio}
            onChange={(e) =>
              setForm((f) => ({ ...f, defaultAspectRatio: e.target.value as "16:9" | "9:16" | "4:3" }))
            }
          >
            <option value="16:9">16:9</option>
            <option value="9:16">9:16</option>
            <option value="4:3">4:3</option>
          </select>
        </div>

        <div className="settings-page__actions">
          <button type="submit" className="settings-page__submit">
            {saved ? "已保存" : "保存配置"}
          </button>
        </div>
      </form>
    </div>
  );
}
