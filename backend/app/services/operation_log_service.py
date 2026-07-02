from app.repositories.mock.operation_log_mock import MockOperationLogRepository


class OperationLogService:
    def __init__(self):
        self.logs = MockOperationLogRepository()

    def write(self, user_id: int, home_id: int | None, action: str, description: str, target_type: str | None = None, target_id: int | None = None) -> dict:
        return self.logs.write(user_id, home_id, action, description, target_type, target_id).__dict__

    def list_by_home(self, home_id: int) -> list[dict]:
        return [log.__dict__ for log in self.logs.list_by_home(home_id)]