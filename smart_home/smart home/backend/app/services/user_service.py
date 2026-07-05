from app.core.security import hash_password, verify_password
from app.repositories.mock.user_mock import MockUserRepository
from app.services.account_operation_log_service import AccountOperationLogService
from app.utils.response import AppException


class UserService:
    def __init__(self):
        self.users = MockUserRepository()
        self.logs = AccountOperationLogService()

    def profile(self, user_id: int) -> dict:
        user = self.users.find_by_id(user_id)
        if not user:
            raise AppException(404, "user not found")
        return {
            "user_id": user.user_id,
            "username": user.username,
            "phone": user.phone,
            "role": user.role,
            "phone_verified": user.phone_verified,
            "phone_bound": user.phone_verified,
        }

    def change_password(self, user_id: int, old_password: str, new_password: str) -> dict:
        user = self.users.find_by_id(user_id)
        if not user or not verify_password(old_password, user.password_hash):
            raise AppException(400, "old password incorrect")
        self.users.update_password(user_id, hash_password(new_password))
        self.logs.write(user_id, None, "CHANGE_PASSWORD", "change password", "USER", user_id)
        return {"status": "password_updated"}
