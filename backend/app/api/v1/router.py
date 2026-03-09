from fastapi import APIRouter

from .export import router as export_router
from .tasks import router as tasks_router
from .test import router as test_router
from .upload import router as upload_router
from .websocket import router as websocket_router


router = APIRouter()

router.include_router(upload_router)
router.include_router(tasks_router)
router.include_router(export_router)
router.include_router(websocket_router)
router.include_router(test_router)
