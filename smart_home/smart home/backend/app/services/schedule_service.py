from typing import Any

from app.core.exceptions import BusinessException
from app.repositories.device_repository import DeviceRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.services.operation_log_service import OperationLogService


class ScheduleService:
    ALLOWED_STATUSES = {"enabled", "disabled", "done", "failed"}
    SWITCHABLE_STATUSES = {"enabled", "disabled"}

    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        device_repository: DeviceRepository,
        operation_log_service: OperationLogService,
    ):
        self.schedule_repository = schedule_repository
        self.device_repository = device_repository
        self.operation_log_service = operation_log_service

    def list_schedules(self, home_id: int) -> list[dict[str, Any]]:
        return self.schedule_repository.list_by_home(home_id)

    def create_schedule(self, home_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        device_id = int(data.get("device_id") or 0)
        self._get_device_for_home(device_id, home_id)

        status = self._clean_optional(data.get("status")) or "enabled"
        self._validate_status(status)

        payload = {
            "device_id": device_id,
            "task_name": self._clean_required(data.get("task_name"), "task_name 不能为空"),
            "execute_time": self._clean_required(data.get("execute_time"), "execute_time 不能为空"),
            "action": self._clean_required(data.get("action"), "action 不能为空"),
            "status": status,
        }
        created = self.schedule_repository.create(home_id, payload)
        self._write_log(
            home_id=home_id,
            operator_id=operator_id,
            operation_type="schedule_create",
            operation_object=f"schedule:{created['task_id']}",
            operation_desc=f"新增定时任务：{created['task_name']}",
        )
        return created

    def update_schedule(self, task_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        current = self.schedule_repository.get(task_id)
        if current is None:
            raise BusinessException("定时任务不存在", 404)

        payload: dict[str, Any] = {}
        if "device_id" in data:
            device_id = int(data.get("device_id") or 0)
            self._get_device_for_home(device_id, current["home_id"])
            payload["device_id"] = device_id
        if "task_name" in data:
            payload["task_name"] = self._clean_required(data.get("task_name"), "task_name 不能为空")
        if "execute_time" in data:
            payload["execute_time"] = self._clean_required(
                data.get("execute_time"), "execute_time 不能为空"
            )
        if "action" in data:
            payload["action"] = self._clean_required(data.get("action"), "action 不能为空")
        if "status" in data:
            status = self._clean_required(data.get("status"), "status 不能为空")
            self._validate_status(status)
            payload["status"] = status

        updated = self.schedule_repository.update(task_id, payload)
        if updated is None:
            raise BusinessException("定时任务不存在", 404)
        self._write_log(
            home_id=updated["home_id"],
            operator_id=operator_id,
            operation_type="schedule_update",
            operation_object=f"schedule:{task_id}",
            operation_desc=f"修改定时任务：{updated['task_name']}",
        )
        return updated

    def update_schedule_status(self, task_id: int, status: str, operator_id: int) -> dict[str, Any]:
        current = self.schedule_repository.get(task_id)
        if current is None:
            raise BusinessException("定时任务不存在", 404)

        normalized = self._clean_required(status, "status 不能为空")
        if normalized not in self.SWITCHABLE_STATUSES:
            raise BusinessException("定时任务状态只能切换为 enabled 或 disabled", 400)

        updated = self.schedule_repository.update(task_id, {"status": normalized})
        if updated is None:
            raise BusinessException("定时任务不存在", 404)
        self._write_log(
            home_id=updated["home_id"],
            operator_id=operator_id,
            operation_type="schedule_status_update",
            operation_object=f"schedule:{task_id}",
            operation_desc=f"定时任务状态切换为：{normalized}",
        )
        return updated

    def delete_schedule(self, task_id: int, operator_id: int) -> dict[str, int]:
        task = self.schedule_repository.get(task_id)
        if task is None:
            raise BusinessException("定时任务不存在", 404)
        self.schedule_repository.delete(task_id)
        self._write_log(
            home_id=task["home_id"],
            operator_id=operator_id,
            operation_type="schedule_delete",
            operation_object=f"schedule:{task_id}",
            operation_desc=f"删除定时任务：{task['task_name']}",
        )
        return {"task_id": task_id}

    def _get_device_for_home(self, device_id: int, home_id: int) -> dict[str, Any]:
        device = self.device_repository.get(device_id)
        if device is None:
            raise BusinessException("定时任务绑定的设备不存在", 404)
        if device["home_id"] != home_id:
            raise BusinessException("定时任务绑定的设备不属于当前家庭空间", 400)
        return device

    def _validate_status(self, status: str) -> None:
        if status not in self.ALLOWED_STATUSES:
            raise BusinessException("定时任务状态不合法", 400)

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
