from typing import Literal

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=6, max_length=64)


class LoginRequest(BaseModel):
    phone: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=64)


class SmsCodeSendRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=20)
    scene: Literal["login", "bind"] = "login"


class SmsLoginRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=20)
    code: str = Field(min_length=4, max_length=8)


class BindPhoneRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=20)
    code: str = Field(min_length=4, max_length=8)


class UserInfo(BaseModel):
    user_id: int
    username: str
    phone: str
    role: str
    phone_verified: bool = False
    phone_bound: bool = False


class LoginData(BaseModel):
    token: str
    user: UserInfo
