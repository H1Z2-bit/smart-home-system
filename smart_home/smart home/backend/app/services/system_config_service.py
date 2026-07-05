from app.core.permissions import Permission
from app.repositories.factory import get_system_config_repository
from app.services.account_operation_log_service import AccountOperationLogService
from app.services.permission_service import PermissionService


class SystemConfigService:
    def __init__(self):
        self.configs = get_system_config_repository()
        self.permissions = PermissionService()
        self.logs = AccountOperationLogService()

    def get_config(self, home_id: int, user_id: int) -> dict:
        self.permissions.require_home_permission(home_id, user_id, Permission.HOME_VIEW)
        return self.configs.get_by_home(home_id).__dict__

    def update_config(self, home_id: int, user_id: int, **kwargs) -> dict:
        self.permissions.require_home_permission(home_id, user_id, Permission.SYSTEM_CONFIG)
        config = self.configs.update(home_id, **kwargs)
        self.logs.write(user_id, home_id, "UPDATE_SYSTEM_CONFIG", "update system config", "SYSTEM_CONFIG", home_id)
        return config.__dict__

    def list_logs(self, home_id: int, user_id: int) -> list[dict]:
        self.permissions.require_home_permission(home_id, user_id, Permission.LOG_VIEW)
        return self.logs.list_by_home(home_id)
