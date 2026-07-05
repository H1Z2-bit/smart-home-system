from typing import Any

from app.core.exceptions import BusinessException
from app.repositories.device_repository import DeviceRepository
from app.repositories.scene_repository import SceneRepository
from app.services.operation_log_service import OperationLogService


class SceneService:
    CONTROLLABLE_TYPES = {"light", "socket"}
    SWITCH_STATES = {"on", "off"}

    def __init__(
        self,
        scene_repository: SceneRepository,
        device_repository: DeviceRepository,
        operation_log_service: OperationLogService,
    ):
        self.scene_repository = scene_repository
        self.device_repository = device_repository
        self.operation_log_service = operation_log_service

    def list_scenes(self, home_id: int) -> list[dict[str, Any]]:
        return self.scene_repository.list_by_home(home_id)

    def create_scene(self, home_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        scene_name = self._clean_required(data.get("scene_name"), "scene_name 不能为空")
        if self.scene_repository.exists_name(home_id, scene_name):
            raise BusinessException("同一家庭空间下情景名称不能重复", 409)

        payload = {
            "scene_name": scene_name,
            "enabled": bool(data.get("enabled", True)),
            "actions": self._normalize_actions(home_id, data.get("actions") or []),
        }
        created = self.scene_repository.create(home_id, payload)
        self._write_log(
            home_id=home_id,
            operator_id=operator_id,
            operation_type="scene_create",
            operation_object=f"scene:{created['scene_id']}",
            operation_desc=f"新增情景模式：{created['scene_name']}",
        )
        return created

    def update_scene(self, scene_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        current = self.scene_repository.get(scene_id)
        if current is None:
            raise BusinessException("情景模式不存在", 404)

        payload: dict[str, Any] = {}
        if "scene_name" in data:
            scene_name = self._clean_required(data.get("scene_name"), "scene_name 不能为空")
            if self.scene_repository.exists_name(
                current["home_id"], scene_name, exclude_scene_id=scene_id
            ):
                raise BusinessException("同一家庭空间下情景名称不能重复", 409)
            payload["scene_name"] = scene_name

        if "enabled" in data:
            payload["enabled"] = bool(data.get("enabled"))

        if "actions" in data:
            payload["actions"] = self._normalize_actions(current["home_id"], data.get("actions") or [])

        updated = self.scene_repository.update(scene_id, payload)
        if updated is None:
            raise BusinessException("情景模式不存在", 404)
        self._write_log(
            home_id=updated["home_id"],
            operator_id=operator_id,
            operation_type="scene_update",
            operation_object=f"scene:{scene_id}",
            operation_desc=f"修改情景模式：{updated['scene_name']}",
        )
        return updated

    def delete_scene(self, scene_id: int, operator_id: int) -> dict[str, int]:
        scene = self.scene_repository.get(scene_id)
        if scene is None:
            raise BusinessException("情景模式不存在", 404)
        self.scene_repository.delete(scene_id)
        self._write_log(
            home_id=scene["home_id"],
            operator_id=operator_id,
            operation_type="scene_delete",
            operation_object=f"scene:{scene_id}",
            operation_desc=f"删除情景模式：{scene['scene_name']}",
        )
        return {"scene_id": scene_id}

    def execute_scene(self, scene_id: int, operator_id: int) -> dict[str, Any]:
        scene = self.scene_repository.get(scene_id)
        if scene is None:
            raise BusinessException("情景模式不存在", 404)
        if not scene.get("enabled", True):
            raise BusinessException("情景模式未启用", 400)

        results = []
        actions = sorted(scene.get("actions", []), key=lambda item: item.get("sort_no", 1))
        for action in actions:
            device_id = int(action["device_id"])
            target_state = str(action["target_state"]).strip().lower()
            device = self.device_repository.get(device_id)
            if device is None:
                results.append(
                    {
                        "device_id": device_id,
                        "success": False,
                        "message": "设备不存在",
                    }
                )
                continue

            if not self._is_controllable(device):
                results.append(
                    {
                        "device_id": device_id,
                        "success": False,
                        "message": "该设备类型暂不支持情景控制",
                    }
                )
                continue

            updated = self.device_repository.update_status(device_id, target_state)
            results.append(
                {
                    "device_id": device_id,
                    "device_name": updated["device_name"] if updated else device["device_name"],
                    "target_state": target_state,
                    "success": updated is not None,
                    "message": "success" if updated else "设备状态更新失败",
                }
            )

        self._write_log(
            home_id=scene["home_id"],
            operator_id=operator_id,
            operation_type="scene_execute",
            operation_object=f"scene:{scene_id}",
            operation_desc=f"执行情景模式：{scene['scene_name']}",
        )
        return {"scene_id": scene_id, "scene_name": scene["scene_name"], "results": results}

    def _normalize_actions(self, home_id: int, actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not actions:
            raise BusinessException("情景模式至少需要一个执行动作", 400)

        normalized = []
        for index, action in enumerate(actions, start=1):
            device_id = int(action.get("device_id") or 0)
            device = self.device_repository.get(device_id)
            if device is None:
                raise BusinessException("情景动作中的设备不存在", 404)
            if device["home_id"] != home_id:
                raise BusinessException("情景动作中的设备不属于当前家庭空间", 400)
            if not self._is_controllable(device):
                raise BusinessException("情景模式暂只支持 light 和 socket 设备", 400)

            target_state = self._clean_required(action.get("target_state"), "target_state 不能为空").lower()
            if target_state not in self.SWITCH_STATES:
                raise BusinessException("情景模式当前仅支持 on/off 状态", 400)

            normalized.append(
                {
                    "device_id": device_id,
                    "target_state": target_state,
                    "param_value": action.get("param_value"),
                    "sort_no": int(action.get("sort_no") or index),
                }
            )
        return normalized

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

    def _is_controllable(self, device: dict[str, Any]) -> bool:
        return str(device.get("device_type", "")).strip() in self.CONTROLLABLE_TYPES

    @staticmethod
    def _clean_required(value: Any, message: str) -> str:
        cleaned = str(value or "").strip()
        if not cleaned:
            raise BusinessException(message, 400)
        return cleaned
