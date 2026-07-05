from typing import Any

from sqlalchemy import desc, select

from app.models.device import DeviceEvent
from app.repositories.device_event_repository import DeviceEventRepository
from app.repositories.mysql.base import flush_refresh, model_to_dict, session_scope


class MySQLDeviceEventRepository(DeviceEventRepository):
    def list_by_device(self, device_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            events = session.scalars(
                select(DeviceEvent)
                .where(DeviceEvent.device_id == device_id)
                .order_by(desc(DeviceEvent.created_at), desc(DeviceEvent.event_id))
            ).all()
            return [model_to_dict(event) for event in events]

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            event = DeviceEvent(
                home_id=data["home_id"],
                device_id=data["device_id"],
                event_type=data["event_type"],
                old_status=data.get("old_status"),
                new_status=data.get("new_status"),
                event_desc=data.get("event_desc"),
                operator_id=data.get("operator_id"),
            )
            flush_refresh(session, event)
            return model_to_dict(event)
