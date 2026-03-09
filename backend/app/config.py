from pydantic_settings import BaseSettings
from pydantic import computed_field


def _parse_comma_list(s: str) -> list[str]:
    """将 .env 中的逗号分隔字符串解析为 list[str]。"""
    return [x.strip() for x in s.split(",") if x.strip()] if s else []


class Settings(BaseSettings):
    # 版面 OCR 后端：gemini | glm（智谱）
    LAYOUT_OCR_PROVIDER: str = "gemini"
    # V2 版面解析（analyze_layout_v2）：Gemini 是否启用 response_schema 强制 JSON 结构，默认 True；失败时自动回退为仅 Few-Shot
    LAYOUT_OCR_V2_STRUCTURED_OUTPUT: bool = True
    GEMINI_API_KEY: str = ""
    GEMINI_LAYOUT_MODEL: str = "gemini-2.5-flash"
    GEMINI_MAX_RPM: int = 15
    # 智谱 GLM（open.bigmodel.cn），可选替代 Gemini 做版面 OCR
    GLM_API_KEY: str = ""
    GLM_LAYOUT_MODEL: str = "glm-4v-plus"
    GLM_API_BASE: str = "https://open.bigmodel.cn/api/paas/v4"
    GLM_MAX_RPM: int = 60
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    # 从 .env 读为字符串（逗号分隔），通过属性访问列表
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png,webp,bmp"
    CORS_ORIGINS: str = "*"
    LOG_LEVEL: str = "INFO"
    WORKERS: int = 2
    TASK_TIMEOUT: int = 3600
    PIPELINE_MAX_WORKERS: int = 3

    @computed_field
    @property
    def allowed_extensions_list(self) -> list[str]:
        return _parse_comma_list(self.ALLOWED_EXTENSIONS) or [
            "pdf", "jpg", "jpeg", "png", "webp", "bmp"
        ]

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return _parse_comma_list(self.CORS_ORIGINS) or ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
