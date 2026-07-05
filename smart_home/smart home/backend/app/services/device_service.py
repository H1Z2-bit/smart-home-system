from typing import Any

from app.core.exceptions import BusinessException
from app.repositories.device_event_repository import DeviceEventRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.room_repository import RoomRepository
from app.services.operation_log_service import OperationLogService


class DeviceService:
    CONTROLLABLE_TYPES = {"light", "socket"}
    SENSOR_TYPES = {"temperature_sensor", "smoke_sensor", "gas_sensor", "door_sensor"}
    SWITCH_STATES = {"on", "off"}
    SWITCH_ACTIONS = {"switch", "control", "set_state"}

    def __init__(
        self,
        device_repository: DeviceRepository,
        room_repository: RoomRepository,
        device_event_repository: DeviceEventRepository,
        operation_log_service: OperationLogService,
    ):
        self.device_repository = device_repository
        self.room_repository = room_repository
        self.device_event_repository = device_event_repository
        self.operation_log_service = operation_log_service

    def list_devices(self, home_id: int, room_id: int | None = None) -> list[dict[str, Any]]:
        if room_id is not None:
            room = self._get_room_or_error(room_id)
            if room["home_id"] != home_id:
                raise BusinessException("房间不属于当前家庭空间", 400)
        return self.device_repository.list_by_home(home_id, room_id)

    def get_device(self, device_id: int) -> dict[str, Any]:
        device = self.device_repository.get(device_id)
        if device is None:
            raise BusinessException("设备不存在", 404)
        return device

    def create_device(self, home_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        room_id = int(data["room_id"])
        room = self._get_room_or_error(room_id)
        if room["home_id"] != home_id:
            raise BusinessException("房间不属于当前家庭空间", 400)

        device_name = self._clean_required(data.get("device_name"), "device_name 不能为空")
        device_type = self._clean_required(data.get("device_type"), "device_type 不能为空")
        if self.device_repository.exists_name(room_id, device_name):
            raise BusinessException("同一房间下设备名称不能重复", 409)

        payload = {
            "room_id": room_id,
            "device_name": device_name,
            "device_type": device_type,
            "device_status": self._clean_optional(data.get("device_status")) or "offline",
            "is_key_device": bool(data.get("is_key_device", False)),
        }
        created = self.device_repository.create(home_id, payload)
        self._write_log(
            home_id=home_id,
            operator_id=operator_id,
            operation_type="device_create",
            operation_object=f"device:{created['device_id']}",
            operation_desc=f"新增设备：{created['device_name']}",
        )
        return created

    def update_device(self, device_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        current = self.device_repository.get(device_id)
        if current is None:
            raise BusinessException("设备不存在", 404)

        room_id = data.get("room_id", current["room_id"])
        room = self._get_room_or_error(int(room_id))

        device_name = data.get("device_name")
        if device_name is not None:
            device_name = self._clean_required(device_name, "device_name 不能为空")
        else:
            device_name = current["device_name"]

        device_type = data.get("device_type")
        if device_type is not None:
            device_type = self._clean_required(device_type, "device_type 不能为空")
        else:
            device_type = current["device_type"]

        if self.device_repository.exists_name(int(room_id), device_name, exclude_device_id=device_id):
            raise BusinessException("同一房间下设备名称不能重复", 409)

        payload = {
            "room_id": int(room_id),
            "device_name": device_name,
            "device_type": device_type,
            "device_status": self._clean_optional(data.get("device_status")) or current["device_status"],
            "is_key_device": data.get("is_key_device", current["is_key_device"]),
        }
        updated = self.device_repository.update(device_id, payload)
        if updated is None:
            raise BusinessException("设备不存在", 404)
        updated["home_id"] = room["home_id"]
        self._write_log(
            home_id=updated["home_id"],
            operator_id=operator_id,
            operation_type="device_update",
            operation_object=f"device:{device_id}",
            operation_desc=f"修改设备：{updated['device_name']}",
        )
        return updated

    def delete_device(self, device_id: int, operator_id: int) -> dict[str, int]:
        device = self.device_repository.get(device_id)
        if device is None:
            raise BusinessException("设备不存在", 404)
        self.device_repository.delete(device_id)
        self._write_log(
            home_id=device["home_id"],
            operator_id=operator_id,
            operation_type="device_delete",
            operation_object=f"device:{device_id}",
            operation_desc=f"删除设备：{device['device_name']}",
        )
        return {"device_id": device_id}

    def control_device(self, device_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        device = self.device_repository.get(device_id)
        if device is None:
            raise BusinessException("设备不存在", 404)

        device_type = str(device.get("device_type", "")).strip()
        if device_type in self.SENSOR_TYPES or device_type.endswith("_sensor"):
            raise BusinessException("传感器类设备不允许控制", 400)
        if device_type not in self.CONTROLLABLE_TYPES:
            raise BusinessException("该设备类型暂不支持控制", 400)

        action = self._clean_required(data.get("action"), "action 不能为空").lower()
        target_state = self._clean_required(data.get("target_state"), "target_state 不能为空").lower()

        if action not in self.SWITCH_ACTIONS:
            raise BusinessException("当前仅支持 switch/control/set_state 控制动作", 400)
        if target_state not in self.SWITCH_STATES:
            raise BusinessException("light 和 socket 仅支持 on/off 状态", 400)

        old_status = device.get("device_status")
        updated = self.device_repository.update_status(device_id, target_state)
        if updated is None:
            raise BusinessException("设备不存在", 404)
        self.device_event_repository.create(
            {
                "home_id": updated["home_id"],
                "device_id": device_id,
                "event_type": "control",
                "old_status": old_status,
                "new_status": updated["device_status"],
                "event_desc": f"控制设备 {updated['device_name']}：{old_status} -> {updated['device_status']}",
                "operator_id": operator_id,
            }
        )
        self._write_log(
            home_id=updated["home_id"],
            operator_id=operator_id,
            operation_type="device_control",
            operation_object=f"device:{device_id}",
            operation_desc=f"控制设备 {updated['device_name']}，目标状态：{target_state}",
        )
        return updated

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

    def _get_room_or_error(self, room_id: int) -> dict[str, Any]:
        room = self.room_repository.get(room_id)
        if room is None:
            raise BusinessException("所属房间不存在", 404)
        return room

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
