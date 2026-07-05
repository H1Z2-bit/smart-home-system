from fastapi import APIRouter

from app.core.config import get_settings
from app.utils.response import success_response

router = APIRouter(tags=["系统"])


@router.get("/health", summary="健康检查")
def health_check() -> dict:
    settings = get_settings()
    return success_response(
        {
            "status": "ok",
            "service": settings.app_name,
            "env": settings.app_env,
        }
    )
