from typing import Any

from app.repositories.operation_log_repository import OperationLogRepository


class OperationLogService:
    def __init__(self, operation_log_repository: OperationLogRepository):
        self.operation_log_repository = operation_log_repository

    def list_logs(self, home_id: int) -> list[dict[str, Any]]:
        return self.operation_log_repository.list_by_home(home_id)

    def write_log(
        self,
        home_id: int,
        operator_id: int,
        operation_type: str,
        operation_object: str,
        operation_result: str,
        operation_desc: str | None = None,
    ) -> dict[str, Any]:
        return self.operation_log_repository.create(
            {
                "home_id": home_id,
                "operator_id": operator_id,
                "operation_type": operation_type,
                "operation_object": operation_object,
                "operation_result": operation_result,
                "operation_desc": operation_desc,
            }
        )
