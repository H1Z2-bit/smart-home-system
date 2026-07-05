from typing import Any

from app.core.exceptions import BusinessException
from app.repositories.device_repository import DeviceRepository
from app.repositories.self_check_repository import SelfCheckRepository
from app.services.operation_log_service import OperationLogService


class SelfCheckService:
    def __init__(
        self,
        self_check_repository: SelfCheckRepository,
        device_repository: DeviceRepository,
        operation_log_service: OperationLogService,
    ):
        self.self_check_repository = self_check_repository
        self.device_repository = device_repository
        self.operation_log_service = operation_log_service

    def list_self_checks(self, device_id: int) -> list[dict[str, Any]]:
        self._get_device_or_error(device_id)
        return self.self_check_repository.list_by_device(device_id)

    def start_self_check(self, device_id: int, operator_id: int) -> dict[str, Any]:
        device = self._get_device_or_error(device_id)
        check_result, error_info = self._evaluate_device(device)
        record = self.self_check_repository.create(
            {
                "device_id": device_id,
                "check_type": "manual",
                "check_result": check_result,
                "error_info": error_info,
                "operator_id": operator_id,
            }
        )
        self.operation_log_service.write_log(
            home_id=device["home_id"],
            operator_id=operator_id,
            operation_type="device_self_check",
            operation_object=f"device:{device_id}",
            operation_result="success",
            operation_desc=f"设备自检：{device['device_name']}，结果：{check_result}",
        )
        return record

    def _get_device_or_error(self, device_id: int) -> dict[str, Any]:
        device = self.device_repository.get(device_id)
        if device is None:
            raise BusinessException("设备不存在", 404)
        return device

    @staticmethod
    def _evaluate_device(device: dict[str, Any]) -> tuple[str, str | None]:
        status = str(device.get("device_status", "")).strip().lower()
        if status == "offline":
            return "offline", "设备离线，无法完成自检"
        if status == "fault":
            return "fault", "设备状态异常，需要维护"
        return "normal", None
