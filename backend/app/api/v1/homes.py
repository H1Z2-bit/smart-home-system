from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.security import TokenPayload
from app.schemas.home import HomeCreateRequest, HomeUpdateRequest
from app.services.home_service import HomeService
from app.utils.response import success

router = APIRouter(prefix="/homes", tags=["家庭空间"])


@router.post("")
def create_home(payload: HomeCreateRequest, current_user: TokenPayload = Depends(get_current_user)):
    return success(HomeService().create_home(current_user.user_id, payload.name, payload.address))


@router.get("")
def list_homes(current_user: TokenPayload = Depends(get_current_user)):
    return success(HomeService().list_homes(current_user.user_id))


@router.get("/{home_id}")
def get_home(home_id: int, current_user: TokenPayload = Depends(get_current_user)):
    return success(HomeService().get_home(home_id, current_user.user_id))


@router.put("/{home_id}")
def update_home(home_id: int, payload: HomeUpdateRequest, current_user: TokenPayload = Depends(get_current_user)):
    return success(HomeService().update_home(home_id, current_user.user_id, payload.name, payload.address))


@router.delete("/{home_id}")
def delete_home(home_id: int, current_user: TokenPayload = Depends(get_current_user)):
    return success(HomeService().delete_home(home_id, current_user.user_id))