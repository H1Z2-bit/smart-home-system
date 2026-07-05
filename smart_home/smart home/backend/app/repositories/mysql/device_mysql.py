from typing import Any

from sqlalchemy import func, select

from app.models.device import Device, DeviceLayout, RoomArea
from app.repositories.device_repository import DeviceRepository
from app.repositories.mysql.base import flush_refresh, model_to_dict, session_scope


class MySQLDeviceRepository(DeviceRepository):
    def list_by_home(self, home_id: int, room_id: int | None = None) -> list[dict[str, Any]]:
        with session_scope() as session:
            query = select(Device).where(Device.home_id == home_id)
            if room_id is not None:
                query = query.where(Device.room_id == room_id)
            devices = session.scalars(query.order_by(Device.device_id)).all()
            return [self._device_dict(session, device) for device in devices]

    def get(self, device_id: int) -> dict[str, Any] | None:
        with session_scope() as session:
            device = session.get(Device, device_id)
            return self._device_dict(session, device) if device else None

    def exists_name(self, room_id: int, device_name: str, exclude_device_id: int | None = None) -> bool:
        with session_scope() as session:
            query = select(Device).where(Device.room_id == room_id, Device.device_name == device_name.strip())
            if exclude_device_id is not None:
                query = query.where(Device.device_id != exclude_device_id)
            return session.scalar(query.limit(1)) is not None

    def count_by_room(self, room_id: int) -> int:
        with session_scope() as session:
            return int(session.scalar(select(func.count()).select_from(Device).where(Device.room_id == room_id)) or 0)

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            device = Device(
                home_id=home_id,
                room_id=data["room_id"],
                device_name=data["device_name"],
                device_type=data["device_type"],
                device_status=data.get("device_status") or "offline",
                is_key_device=bool(data.get("is_key_device", False)),
            )
            flush_refresh(session, device)
            return self._device_dict(session, device)

    def update(self, device_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        with session_scope() as session:
            device = session.get(Device, device_id)
            if device is None:
                return None
            for key in ["room_id", "device_name", "device_type", "device_status", "is_key_device"]:
                if key in data and data[key] is not None:
                    setattr(device, key, data[key])
            room = session.get(RoomArea, device.room_id)
            if room is not None:
                device.home_id = room.home_id
            session.flush()
            session.refresh(device)
            return self._device_dict(session, device)

    def update_status(self, device_id: int, device_status: str) -> dict[str, Any] | None:
        with session_scope() as session:
            device = session.get(Device, device_id)
            if device is None:
                return None
            device.device_status = device_status
            session.flush()
            session.refresh(device)
            return self._device_dict(session, device)

    def delete(self, device_id: int) -> bool:
        with session_scope() as session:
            device = session.get(Device, device_id)
            if device is None:
                return False
            session.delete(device)
            return True

    @staticmethod
    def _device_dict(session, device: Device) -> dict[str, Any]:
        layout = session.scalar(select(DeviceLayout).where(DeviceLayout.device_id == device.device_id))
        return model_to_dict(device, {"layout": model_to_dict(layout) if layout else None})
