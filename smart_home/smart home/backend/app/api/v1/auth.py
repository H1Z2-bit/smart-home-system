from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.security import TokenPayload
from app.schemas.auth import BindPhoneRequest, ChangePasswordRequest, LoginRequest, RegisterRequest, SmsCodeSendRequest, SmsLoginRequest
from app.services.auth_service import AuthService
from app.services.sms_auth_service import SmsAuthService
from app.services.user_service import UserService
from app.utils.response import AppException, success

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
def register(payload: RegisterRequest):
    data = AuthService().register(payload.username, payload.phone, payload.password)
    return success(data)


@router.post("/login")
def login(payload: LoginRequest):
    data = AuthService().login(payload.phone, payload.password)
    return success(data)


@router.post("/sms/send")
def send_sms_code(payload: SmsCodeSendRequest):
    if payload.scene != "login":
        raise AppException(400, "public sms endpoint only supports login scene")
    data = SmsAuthService().send_code(payload.phone, payload.scene)
    return success(data)


@router.post("/sms/login")
def sms_login(payload: SmsLoginRequest):
    data = SmsAuthService().login_with_code(payload.phone, payload.code)
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


@user_router.post("/phone/code")
def send_bind_phone_code(payload: SmsCodeSendRequest, current_user: TokenPayload = Depends(get_current_user)):
    data = SmsAuthService().send_code(payload.phone, "bind")
    return success(data)


@user_router.post("/phone/bind")
def bind_phone(payload: BindPhoneRequest, current_user: TokenPayload = Depends(get_current_user)):
    data = SmsAuthService().bind_phone(current_user.user_id, payload.phone, payload.code)
    return success(data)
