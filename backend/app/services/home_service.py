from app.core.permissions import Permission
from app.repositories.mock.home_mock import MockHomeRepository
from app.repositories.mock.user_mock import MockUserRepository
from app.services.operation_log_service import OperationLogService
from app.services.permission_service import PermissionService
from app.utils.response import AppException


class HomeService:
    def __init__(self):
        self.homes = MockHomeRepository()
        self.users = MockUserRepository()
        self.permissions = PermissionService()
        self.logs = OperationLogService()

    def _require_member(self, home_id: int, user_id: int):
        return self.permissions.require_home_member(home_id, user_id)

    def _require_owner(self, home_id: int, user_id: int):
        return self.permissions.require_home_owner(home_id, user_id)

    def create_home(self, user_id: int, name: str, address: str | None) -> dict:
        user = self.users.find_by_id(user_id)
        if not user:
            raise AppException(404, "user not found")
        home = self.homes.create(user_id, user.username, user.phone, name, address)
        self.logs.write(user_id, home.home_id, "CREATE_HOME", "create home", "HOME", home.home_id)
        return home.__dict__

    def list_homes(self, user_id: int) -> list[dict]:
        return [home.__dict__ for home in self.homes.list_by_user(user_id)]

    def get_home(self, home_id: int, user_id: int) -> dict:
        self.permissions.require_home_permission(home_id, user_id, Permission.HOME_VIEW)
        home = self.homes.find_by_id(home_id)
        if not home:
            raise AppException(404, "home not found")
        return home.__dict__

    def update_home(self, home_id: int, user_id: int, name: str | None, address: str | None) -> dict:
        self.permissions.require_home_permission(home_id, user_id, Permission.HOME_MANAGE)
        home = self.homes.update(home_id, name, address)
        if not home:
            raise AppException(404, "home not found")
        self.logs.write(user_id, home_id, "UPDATE_HOME", "update home", "HOME", home_id)
        return home.__dict__

    def delete_home(self, home_id: int, user_id: int) -> dict:
        self.permissions.require_home_permission(home_id, user_id, Permission.HOME_MANAGE)
        if not self.homes.delete(home_id):
            raise AppException(404, "home not found")
        self.logs.write(user_id, home_id, "DELETE_HOME", "delete home", "HOME", home_id)
        return {"status": "deleted"}