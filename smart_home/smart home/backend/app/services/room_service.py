from typing import Any

from app.core.exceptions import BusinessException
from app.repositories.device_repository import DeviceRepository
from app.repositories.room_repository import RoomRepository
from app.services.operation_log_service import OperationLogService


class RoomService:
    def __init__(
        self,
        room_repository: RoomRepository,
        device_repository: DeviceRepository,
        operation_log_service: OperationLogService,
    ):
        self.room_repository = room_repository
        self.device_repository = device_repository
        self.operation_log_service = operation_log_service

    def list_rooms(self, home_id: int) -> list[dict[str, Any]]:
        return self.room_repository.list_by_home(home_id)

    def create_room(self, home_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        room_name = self._clean_required(data.get("room_name"), "room_name 不能为空")
        if self.room_repository.exists_name(home_id, room_name):
            raise BusinessException("同一家庭空间下房间名称不能重复", 409)

        payload = {
            "room_name": room_name,
            "room_type": self._clean_optional(data.get("room_type")),
            "remark": self._clean_optional(data.get("remark")),
        }
        created = self.room_repository.create(home_id, payload)
        self._write_log(
            home_id=home_id,
            operator_id=operator_id,
            operation_type="room_create",
            operation_object=f"room:{created['room_id']}",
            operation_desc=f"新增房间：{created['room_name']}",
        )
        return created

    def update_room(self, room_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        room = self.room_repository.get(room_id)
        if room is None:
            raise BusinessException("房间不存在", 404)

        room_name = self._clean_required(data.get("room_name"), "room_name 不能为空")
        if self.room_repository.exists_name(room["home_id"], room_name, exclude_room_id=room_id):
            raise BusinessException("同一家庭空间下房间名称不能重复", 409)

        payload = {
            "room_name": room_name,
            "room_type": self._clean_optional(data.get("room_type")),
            "remark": self._clean_optional(data.get("remark")),
        }
        updated = self.room_repository.update(room_id, payload)
        if updated is None:
            raise BusinessException("房间不存在", 404)
        self._write_log(
            home_id=updated["home_id"],
            operator_id=operator_id,
            operation_type="room_update",
            operation_object=f"room:{room_id}",
            operation_desc=f"修改房间：{updated['room_name']}",
        )
        return updated

    def delete_room(self, room_id: int, operator_id: int) -> dict[str, int]:
        room = self.room_repository.get(room_id)
        if room is None:
            raise BusinessException("房间不存在", 404)
        if self.device_repository.count_by_room(room_id) > 0:
            raise BusinessException("该房间下存在设备，不能删除", 400)

        self.room_repository.delete(room_id)
        self._write_log(
            home_id=room["home_id"],
            operator_id=operator_id,
            operation_type="room_delete",
            operation_object=f"room:{room_id}",
            operation_desc=f"删除房间：{room['room_name']}",
        )
        return {"room_id": room_id}

    def _write_log(
        self,
        home_id: int,
        operator_id: int,
        operation_type: str,
        operation_object: str,
        operation_desc: str,
    ) -> None:
        self.operation_log_service.write_log(
            home_id=home_id,
            operator_id=operator_id,
            operation_type=operation_type,
            operation_object=operation_object,
            operation_result="success",
            operation_desc=operation_desc,
        )

    @staticmethod
    def _clean_required(value: Any, message: str) -> str:
        cleaned = str(value or "").strip()
        if not cleaned:
            raise BusinessException(message, 400)
        return cleaned

    @staticmethod
    def _clean_optional(value: Any) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None
