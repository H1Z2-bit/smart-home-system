from typing import Any

from sqlalchemy import select

from app.models.device import RoomArea, RoomLayout
from app.repositories.mysql.base import flush_refresh, model_to_dict, session_scope
from app.repositories.room_repository import RoomRepository


class MySQLRoomRepository(RoomRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            rooms = session.scalars(
                select(RoomArea)
                .where(RoomArea.home_id == home_id, RoomArea.status != "DISABLED")
                .order_by(RoomArea.sort_no, RoomArea.room_id)
            ).all()
            return [self._room_dict(session, room) for room in rooms]

    def get(self, room_id: int) -> dict[str, Any] | None:
        with session_scope() as session:
            room = session.get(RoomArea, room_id)
            return self._room_dict(session, room) if room else None

    def exists_name(self, home_id: int, room_name: str, exclude_room_id: int | None = None) -> bool:
        with session_scope() as session:
            query = select(RoomArea).where(RoomArea.home_id == home_id, RoomArea.room_name == room_name.strip())
            if exclude_room_id is not None:
                query = query.where(RoomArea.room_id != exclude_room_id)
            return session.scalar(query.limit(1)) is not None

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            room = RoomArea(
                home_id=home_id,
                room_name=data["room_name"],
                room_type=data.get("room_type"),
                remark=data.get("remark"),
            )
            flush_refresh(session, room)
            return self._room_dict(session, room)

    def update(self, room_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        with session_scope() as session:
            room = session.get(RoomArea, room_id)
            if room is None:
                return None
            room.room_name = data["room_name"]
            room.room_type = data.get("room_type")
            room.remark = data.get("remark")
            session.flush()
            session.refresh(room)
            return self._room_dict(session, room)

    def delete(self, room_id: int) -> bool:
        with session_scope() as session:
            room = session.get(RoomArea, room_id)
            if room is None:
                return False
            session.delete(room)
            return True

    @staticmethod
    def _room_dict(session, room: RoomArea) -> dict[str, Any]:
        layout = session.scalar(select(RoomLayout).where(RoomLayout.room_id == room.room_id))
        return model_to_dict(room, {"layout": model_to_dict(layout) if layout else None})
