from typing import Any

from app.repositories.device_event_repository import DeviceEventRepository
from app.repositories.mock import store


class MockDeviceEventRepository(DeviceEventRepository):
    def list_by_device(self, device_id: int) -> list[dict[str, Any]]:
        return [
            store.copy_record(event)
            for event in sorted(store.device_events, key=lambda item: item["event_id"], reverse=True)
            if event["device_id"] == device_id
        ]

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        event = {
            "event_id": store.next_device_event_id(),
            "home_id": data["home_id"],
            "device_id": data["device_id"],
            "event_type": data["event_type"],
            "old_status": data.get("old_status"),
            "new_status": data.get("new_status"),
            "event_desc": data.get("event_desc"),
            "operator_id": data.get("operator_id"),
            "created_at": store.now_text(),
        }
        store.device_events.append(event)
        return store.copy_record(event)
