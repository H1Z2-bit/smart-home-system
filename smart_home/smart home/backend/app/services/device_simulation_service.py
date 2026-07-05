from typing import Any

from app.core.exceptions import BusinessException
from app.repositories.alarm_repository import AlarmRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.device_simulation_repository import DeviceSimulationRepository
from app.services.operation_log_service import OperationLogService


class DeviceSimulationService:
    SIMULATION_TYPES = {"manual", "auto", "scenario"}

    def __init__(
        self,
        device_simulation_repository: DeviceSimulationRepository,
        device_repository: DeviceRepository,
        alarm_repository: AlarmRepository,
        operation_log_service: OperationLogService,
    ):
        self.device_simulation_repository = device_simulation_repository
        self.device_repository = device_repository
        self.alarm_repository = alarm_repository
        self.operation_log_service = operation_log_service

    def list_simulations(self, device_id: int) -> list[dict[str, Any]]:
        self._get_device_or_error(device_id)
        return self.device_simulation_repository.list_by_device(device_id)

    def create_simulation(self, device_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        device = self._get_device_or_error(device_id)
        metric_name = self._clean_required(data.get("metric_name"), "metric_name 不能为空")
        device_status = self._clean_optional(data.get("device_status"))
        trigger_alarm = bool(data.get("trigger_alarm", False))
        alarm_type = self._clean_optional(data.get("alarm_type"))
        alarm_level = self._clean_optional(data.get("alarm_level")) or "warning"
        simulation_type = self._clean_optional(data.get("simulation_type")) or "manual"
        scenario_name = self._clean_optional(data.get("scenario_name"))
        if simulation_type not in self.SIMULATION_TYPES:
            raise BusinessException("simulation_type 仅支持 manual/auto/scenario", 400)
        if device_status is not None:
            self.device_repository.update_status(device_id, device_status)

        alarm = None
        if trigger_alarm:
            alarm_type = alarm_type or metric_name
            alarm = self.alarm_repository.create(
                {
                    "home_id": device["home_id"],
                    "device_id": device_id,
                    "alarm_type": alarm_type,
                    "alarm_level": alarm_level,
                    "trigger_value": str(data.get("metric_value")),
                    "alarm_status": "new",
                    "process_desc": f"设备模拟触发报警：{device['device_name']} {metric_name}",
                }
            )

        record = self.device_simulation_repository.create(
            {
                "home_id": device["home_id"],
                "device_id": device_id,
                "metric_name": metric_name,
                "metric_value": data.get("metric_value"),
                "device_status": device_status,
                "trigger_alarm": trigger_alarm,
                "alarm_type": alarm_type,
                "alarm_level": alarm_level,
                "alarm_id": alarm["alarm_id"] if alarm else None,
                "simulation_type": simulation_type,
                "scenario_name": scenario_name,
            }
        )
        self.operation_log_service.write_log(
            home_id=device["home_id"],
            operator_id=operator_id,
            operation_type="device_simulate",
            operation_object=f"device:{device_id}",
            operation_result="success",
            operation_desc=f"模拟设备数据：{device['device_name']} {metric_name}={data.get('metric_value')}",
        )
        if alarm is not None:
            record["alarm"] = alarm
        return record

    def _get_device_or_error(self, device_id: int) -> dict[str, Any]:
        device = self.device_repository.get(device_id)
        if device is None:
            raise BusinessException("设备不存在", 404)
        return device

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
