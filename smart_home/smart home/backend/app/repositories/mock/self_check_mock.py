from typing import Any

from app.repositories.mock import store
from app.repositories.self_check_repository import SelfCheckRepository


class MockSelfCheckRepository(SelfCheckRepository):
    def list_by_device(self, device_id: int) -> list[dict[str, Any]]:
        return [
            store.copy_record(record)
            for record in store.self_check_records
            if record["device_id"] == device_id
        ]

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        record = {
            "check_id": store.next_self_check_id(),
            "device_id": data["device_id"],
            "check_type": data.get("check_type", "manual"),
            "check_result": data["check_result"],
            "error_info": data.get("error_info"),
            "check_time": store.now_text(),
            "operator_id": data.get("operator_id", 1),
        }
        store.self_check_records.append(record)
        return store.copy_record(record)
