from fastapi import APIRouter

from app.api.v1 import auth, homes, members, system
from app.utils.response import success

api_router = APIRouter()


@api_router.get("/health", tags=["系统"])
def health_check():
    return success({"status": "ok", "service": "smart-home-python-backend"})


api_router.include_router(auth.router)
api_router.include_router(auth.user_router)
api_router.include_router(homes.router)
api_router.include_router(members.router)
api_router.include_router(system.router)