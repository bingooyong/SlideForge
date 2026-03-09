const STORAGE_KEY = "slideforge_settings";

export interface AppSettings {
  geminiApiKey: string;
  defaultMode: "lite" | "standard";
  defaultAspectRatio: "16:9" | "9:16" | "4:3";
}

const defaults: AppSettings = {
  geminiApiKey: "",
  defaultMode: "standard",
  defaultAspectRatio: "16:9",
};

export function getSettings(): AppSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...defaults };
    const parsed = JSON.parse(raw) as Partial<AppSettings>;
    return {
      geminiApiKey: typeof parsed.geminiApiKey === "string" ? parsed.geminiApiKey : defaults.geminiApiKey,
      defaultMode: parsed.defaultMode === "lite" || parsed.defaultMode === "standard" ? parsed.defaultMode : defaults.defaultMode,
      defaultAspectRatio: parsed.defaultAspectRatio === "16:9" || parsed.defaultAspectRatio === "9:16" || parsed.defaultAspectRatio === "4:3"
        ? parsed.defaultAspectRatio
        : defaults.defaultAspectRatio,
    };
  } catch {
    return { ...defaults };
  }
}

export function saveSettings(settings: Partial<AppSettings>): void {
  const current = getSettings();
  const next: AppSettings = {
    geminiApiKey: typeof settings.geminiApiKey !== "undefined" ? settings.geminiApiKey : current.geminiApiKey,
    defaultMode: settings.defaultMode ?? current.defaultMode,
    defaultAspectRatio: settings.defaultAspectRatio ?? current.defaultAspectRatio,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
}
