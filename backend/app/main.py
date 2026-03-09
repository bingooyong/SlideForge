from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import router
from app.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="SlideForge API",
    description="API for converting images/PDFs to editable PPTX files",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


app.include_router(router, prefix="/api/v1")

# 前端构建产物目录（一键脚本构建后为 backend/static），挂载在最后以便 /api 优先
_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if _STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="frontend")
else:

    @app.get("/")
    async def root():
        return {"message": "SlideForge API", "docs": "/docs"}
