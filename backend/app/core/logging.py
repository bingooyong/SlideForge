from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

import structlog

from app.config import settings


def _ensure_log_dir() -> Path:
    """
    确保日志目录存在，默认使用项目根目录下的 logs/。
    """
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging() -> None:
    """
    初始化全局日志配置：
    - 使用 structlog 输出 JSON 结构化日志；
    - 控制台输出 + 按日期滚动的文件输出：当前文件为 logs/pipeline.log，午夜滚动后历史文件为 logs/pipeline.log.YYYY-MM-DD。
    """
    log_dir = _ensure_log_dir()

    level_name = getattr(settings, "LOG_LEVEL", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    file_handler = TimedRotatingFileHandler(
        filename=str(log_dir / "pipeline.log"),
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.setLevel(level)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO", key="timestamp"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    返回带有模块名绑定字段的 structlog logger。
    """
    logger = structlog.get_logger(name or "app")
    if name:
        logger = logger.bind(logger=name)
    return logger

