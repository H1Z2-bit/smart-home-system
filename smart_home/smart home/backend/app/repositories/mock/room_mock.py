from typing import Any

from app.repositories.mock import store
from app.repositories.room_repository import RoomRepository


class MockRoomRepository(RoomRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        return [
            store.copy_record(room)
            for room in store.rooms.values()
            if room["home_id"] == home_id
        ]

    def get(self, room_id: int) -> dict[str, Any] | None:
        return store.copy_record(store.rooms.get(room_id))

    def exists_name(self, home_id: int, room_name: str, exclude_room_id: int | None = None) -> bool:
        normalized_name = room_name.strip()
        return any(
            room["home_id"] == home_id
            and room["room_name"] == normalized_name
            and room["room_id"] != exclude_room_id
            for room in store.rooms.values()
        )

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        room_id = store.next_room_id()
        room = {
            "room_id": room_id,
            "home_id": home_id,
            "room_name": data["room_name"],
            "room_type": data.get("room_type"),
            "remark": data.get("remark"),
        }
        store.rooms[room_id] = room
        return store.copy_record(room)

    def update(self, room_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        room = store.rooms.get(room_id)
        if room is None:
            return None

        room["room_name"] = data["room_name"]
        room["room_type"] = data.get("room_type")
        room["remark"] = data.get("remark")
        return store.copy_record(room)

    def delete(self, room_id: int) -> bool:
        if room_id not in store.rooms:
            return False
        del store.rooms[room_id]
        return True
