from fastapi import APIRouter
from .auth import router as auth_router
from .plaques import router as plaques_router
from .images import router as images_router
from .categories import router as categories_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(plaques_router)
router.include_router(images_router)
router.include_router(categories_router)
