from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.factory import get_user_repository
from app.services.account_operation_log_service import AccountOperationLogService
from app.utils.response import AppException


class AuthService:
    def __init__(self):
        self.users = get_user_repository()
        self.logs = AccountOperationLogService()

    def register(self, username: str, phone: str, password: str) -> dict:
        if self.users.find_by_phone(phone):
            raise AppException(409, "phone already registered")
        user = self.users.save(username=username, phone=phone, password_hash=hash_password(password))
        self.logs.write(user.user_id, None, "REGISTER", "user register", "USER", user.user_id)
        return {"user_id": user.user_id, "username": user.username}

    def login(self, phone: str, password: str) -> dict:
        user = self.users.find_by_phone(phone)
        if not user or not verify_password(password, user.password_hash):
            raise AppException(401, "phone or password incorrect")
        token = create_access_token(user.user_id, user.username, user.role)
        self.logs.write(user.user_id, None, "LOGIN", "user login", "USER", user.user_id)
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

    def logout(self, user_id: int) -> dict:
        self.logs.write(user_id, None, "LOGOUT", "user logout", "USER", user_id)
        return {"status": "logout_ok"}
