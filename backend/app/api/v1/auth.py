from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.security import TokenPayload
from app.schemas.auth import ChangePasswordRequest, LoginRequest, RegisterRequest
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.response import success

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
def register(payload: RegisterRequest):
    data = AuthService().register(payload.username, payload.phone, payload.password)
    return success(data)


@router.post("/login")
def login(payload: LoginRequest):
    data = AuthService().login(payload.phone, payload.password)
    return success(data)


@router.post("/logout")
def logout(current_user: TokenPayload = Depends(get_current_user)):
    data = AuthService().logout(current_user.user_id)
    return success(data)


user_router = APIRouter(prefix="/users", tags=["用户"])


@user_router.get("/profile")
def profile(current_user: TokenPayload = Depends(get_current_user)):
    data = UserService().profile(current_user.user_id)
    return success(data)


@user_router.put("/password")
def change_password(payload: ChangePasswordRequest, current_user: TokenPayload = Depends(get_current_user)):
    data = UserService().change_password(current_user.user_id, payload.old_password, payload.new_password)
    return success(data)