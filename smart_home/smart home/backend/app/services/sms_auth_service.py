import secrets
import time

from app.core.security import create_access_token, hash_password
from app.repositories.factory import get_sms_code_repository, get_user_repository
from app.services.account_operation_log_service import AccountOperationLogService
from app.utils.response import AppException


class SmsAuthService:
    CODE_TTL_SECONDS = 300
    MAX_ATTEMPTS = 5
    SCENE_LOGIN = "login"
    SCENE_BIND = "bind"

    def __init__(self):
        self.users = get_user_repository()
        self.sms_codes = get_sms_code_repository()
        self.logs = AccountOperationLogService()

    def send_code(self, phone: str, scene: str = SCENE_LOGIN) -> dict:
        if scene not in {self.SCENE_LOGIN, self.SCENE_BIND}:
            raise AppException(400, "invalid sms scene")

        code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = time.time() + self.CODE_TTL_SECONDS
        self.sms_codes.save(phone=phone, scene=scene, code=code, expires_at=expires_at)
        return {
            "phone": phone,
            "scene": scene,
            "expires_in": self.CODE_TTL_SECONDS,
            "mock_code": code,
            "mock_notice": "Mock mode returns the SMS code directly. Real SMS provider must not return it.",
        }

    def login_with_code(self, phone: str, code: str) -> dict:
        self._verify_code(phone, self.SCENE_LOGIN, code)

        user = self.users.find_by_verified_phone(phone)
        if user:
            action = "SMS_LOGIN"
        else:
            user = self.users.find_by_phone(phone)
            if user:
                user = self.users.verify_phone(user.user_id)
                action = "SMS_VERIFY_AND_LOGIN"
            else:
                username = self._make_default_username(phone)
                user = self.users.save(
                    username=username,
                    phone=phone,
                    password_hash=hash_password(secrets.token_urlsafe(24)),
                    phone_verified=True,
                )
                action = "SMS_REGISTER_LOGIN"

        self.sms_codes.mark_used(phone, self.SCENE_LOGIN)
        self.logs.write(user.user_id, None, action, "sms code login", "USER", user.user_id)
        return self._login_data(user)

    def bind_phone(self, user_id: int, phone: str, code: str) -> dict:
        current_user = self.users.find_by_id(user_id)
        if not current_user:
            raise AppException(404, "user not found")

        owner = self.users.find_by_verified_phone(phone)
        if owner and owner.user_id != user_id:
            raise AppException(409, "phone already bound by another account")

        registered_user = self.users.find_by_phone(phone)
        if registered_user and registered_user.user_id != user_id:
            raise AppException(409, "phone already used by another account")

        self._verify_code(phone, self.SCENE_BIND, code)
        user = self.users.bind_phone(user_id, phone)
        self.sms_codes.mark_used(phone, self.SCENE_BIND)
        self.logs.write(user.user_id, None, "BIND_PHONE", "bind verified phone", "USER", user.user_id)
        return {
            "user_id": user.user_id,
            "username": user.username,
            "phone": user.phone,
            "phone_verified": user.phone_verified,
            "phone_bound": user.phone_verified,
        }

    def _verify_code(self, phone: str, scene: str, code: str) -> None:
        sms_code = self.sms_codes.find_latest(phone, scene)
        if not sms_code or sms_code.used:
            raise AppException(400, "sms code invalid")
        if self.sms_codes.is_expired(sms_code):
            raise AppException(400, "sms code expired")
        if sms_code.attempts >= self.MAX_ATTEMPTS:
            raise AppException(429, "sms code attempts exceeded")

        if sms_code.code != code:
            if hasattr(self.sms_codes, "increment_attempts"):
                self.sms_codes.increment_attempts(phone, scene)
            else:
                sms_code.attempts += 1
            raise AppException(400, "sms code incorrect")

    def _login_data(self, user) -> dict:
        token = create_access_token(user.user_id, user.username, user.role)
        return {
            "token": token,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "phone": user.phone,
                "role": user.role,
                "phone_verified": user.phone_verified,
                "phone_bound": user.phone_verified,
            },
        }

    def _make_default_username(self, phone: str) -> str:
        base = f"user_{phone[-4:]}"
        username = base
        index = 1
        while self.users.find_by_username(username):
            index += 1
            username = f"{base}_{index}"
        return username
