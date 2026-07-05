from typing import Any

from app.repositories.device_repository import DeviceRepository
from app.repositories.mock import store


class MockDeviceRepository(DeviceRepository):
    def list_by_home(self, home_id: int, room_id: int | None = None) -> list[dict[str, Any]]:
        result = []
        for device in store.devices.values():
            if device["home_id"] != home_id:
                continue
            if room_id is not None and device["room_id"] != room_id:
                continue
            result.append(store.copy_record(device))
        return result

    def get(self, device_id: int) -> dict[str, Any] | None:
        return store.copy_record(store.devices.get(device_id))

    def exists_name(self, room_id: int, device_name: str, exclude_device_id: int | None = None) -> bool:
        normalized_name = device_name.strip()
        return any(
            device["room_id"] == room_id
            and device["device_name"] == normalized_name
            and device["device_id"] != exclude_device_id
            for device in store.devices.values()
        )

    def count_by_room(self, room_id: int) -> int:
        return sum(1 for device in store.devices.values() if device["room_id"] == room_id)

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        device_id = store.next_device_id()
        device = {
            "device_id": device_id,
            "home_id": home_id,
            "room_id": data["room_id"],
            "device_name": data["device_name"],
            "device_type": data["device_type"],
            "device_status": data.get("device_status") or "offline",
            "is_key_device": data.get("is_key_device", False),
            "created_at": store.now_text(),
        }
        store.devices[device_id] = device
        return store.copy_record(device)

    def update(self, device_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        device = store.devices.get(device_id)
        if device is None:
            return None

        for key in ["room_id", "device_name", "device_type", "device_status", "is_key_device"]:
            if key in data and data[key] is not None:
                device[key] = data[key]

        room = store.rooms.get(device["room_id"])
        if room is not None:
            device["home_id"] = room["home_id"]
        return store.copy_record(device)

    def update_status(self, device_id: int, device_status: str) -> dict[str, Any] | None:
        device = store.devices.get(device_id)
        if device is None:
            return None

        device["device_status"] = device_status
        return store.copy_record(device)

    def delete(self, device_id: int) -> bool:
        if device_id not in store.devices:
            return False
        del store.devices[device_id]
        return True
