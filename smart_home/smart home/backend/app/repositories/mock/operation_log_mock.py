from typing import Any

from app.repositories.mock import store
from app.repositories.operation_log_repository import OperationLogRepository


class MockOperationLogRepository(OperationLogRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        return [
            store.copy_record(log)
            for log in store.operation_logs
            if log["home_id"] == home_id
        ]

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        log = {
            "log_id": store.next_log_id(),
            "home_id": data["home_id"],
            "operator_id": data["operator_id"],
            "operation_type": data["operation_type"],
            "operation_object": data["operation_object"],
            "operation_result": data["operation_result"],
            "operation_desc": data.get("operation_desc"),
            "created_at": store.now_text(),
        }
        store.operation_logs.append(log)
        return store.copy_record(log)
