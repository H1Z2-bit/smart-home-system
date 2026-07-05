from typing import Any

from app.core.exceptions import BusinessException
from app.repositories.alarm_repository import AlarmRepository
from app.services.operation_log_service import OperationLogService


class AlarmService:
    def __init__(
        self,
        alarm_repository: AlarmRepository,
        operation_log_service: OperationLogService,
    ):
        self.alarm_repository = alarm_repository
        self.operation_log_service = operation_log_service

    def list_alarms(self, home_id: int) -> list[dict[str, Any]]:
        return self.alarm_repository.list_by_home(home_id)

    def get_alarm_detail(self, alarm_id: int) -> dict[str, Any]:
        alarm = self.alarm_repository.get(alarm_id)
        if alarm is None:
            raise BusinessException("报警记录不存在", 404)
        alarm["process_logs"] = self.alarm_repository.list_process_logs(alarm_id)
        return alarm

    def confirm_alarm(self, alarm_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        return self._process_alarm(
            alarm_id=alarm_id,
            status="confirmed",
            action_type="confirm",
            default_desc="确认报警",
            data=data,
            operator_id=operator_id,
        )

    def process_alarm(self, alarm_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        return self._process_alarm(
            alarm_id=alarm_id,
            status="processing",
            action_type="process",
            default_desc="处理报警",
            data=data,
            operator_id=operator_id,
        )

    def resolve_alarm(self, alarm_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        return self._process_alarm(
            alarm_id=alarm_id,
            status="closed",
            action_type="close",
            default_desc="关闭报警",
            data=data,
            operator_id=operator_id,
            close_alarm=True,
        )

    def mark_false_alarm(self, alarm_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        return self._process_alarm(
            alarm_id=alarm_id,
            status="false_alarm",
            action_type="mark_false_alarm",
            default_desc="标记为误报",
            data=data,
            operator_id=operator_id,
            close_alarm=True,
        )

    def _process_alarm(
        self,
        alarm_id: int,
        status: str,
        action_type: str,
        default_desc: str,
        data: dict[str, Any],
        operator_id: int,
        close_alarm: bool = False,
    ) -> dict[str, Any]:
        alarm = self.alarm_repository.get(alarm_id)
        if alarm is None:
            raise BusinessException("报警记录不存在", 404)
        if alarm.get("alarm_status") in {"closed", "false_alarm"}:
            raise BusinessException("报警记录已结束，不能重复处理", 400)

        updated = self.alarm_repository.update_status(
            alarm_id,
            status,
            operator_id=operator_id,
            close_alarm=close_alarm,
        )
        if updated is None:
            raise BusinessException("报警记录不存在", 404)

        process_desc = self._clean_optional(data.get("process_desc")) or default_desc
        self.alarm_repository.add_process_log(
            alarm_id,
            {
                "handler_id": operator_id,
                "action_type": action_type,
                "process_desc": process_desc,
                "process_result": self._clean_optional(data.get("process_result")) or "success",
            },
        )
        self.operation_log_service.write_log(
            home_id=updated["home_id"],
            operator_id=operator_id,
            operation_type="alarm_process",
            operation_object=f"alarm:{alarm_id}",
            operation_result="success",
            operation_desc=f"{default_desc}：{process_desc}",
        )
        updated["process_logs"] = self.alarm_repository.list_process_logs(alarm_id)
        return updated

    @staticmethod
    def _clean_optional(value: Any) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None
