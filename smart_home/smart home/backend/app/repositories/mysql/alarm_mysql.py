from typing import Any

from sqlalchemy import select
from sqlalchemy.sql import func

from app.models.alarm import AlarmProcessLog, AlarmRecord
from app.repositories.alarm_repository import AlarmRepository
from app.repositories.mysql.base import flush_refresh, model_to_dict, session_scope


class MySQLAlarmRepository(AlarmRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            alarms = session.scalars(select(AlarmRecord).where(AlarmRecord.home_id == home_id).order_by(AlarmRecord.alarm_id.desc())).all()
            return [model_to_dict(alarm) for alarm in alarms]

    def get(self, alarm_id: int) -> dict[str, Any] | None:
        with session_scope() as session:
            alarm = session.get(AlarmRecord, alarm_id)
            return model_to_dict(alarm) if alarm else None

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            alarm = AlarmRecord(
                home_id=data["home_id"],
                device_id=data["device_id"],
                alarm_type=data["alarm_type"],
                alarm_level=data.get("alarm_level", "warning"),
                trigger_value=str(data.get("trigger_value", "")),
                alarm_status=data.get("alarm_status", "new"),
                alarm_desc=data.get("alarm_desc") or data.get("process_desc"),
            )
            flush_refresh(session, alarm)
            process_log = AlarmProcessLog(
                alarm_id=alarm.alarm_id,
                handler_id=None,
                action_type="notify",
                process_desc=data.get("process_desc", "设备模拟触发报警"),
                process_result="success",
            )
            session.add(process_log)
            return model_to_dict(alarm)

    def update_status(
        self,
        alarm_id: int,
        status: str,
        operator_id: int | None = None,
        close_alarm: bool = False,
    ) -> dict[str, Any] | None:
        with session_scope() as session:
            alarm = session.get(AlarmRecord, alarm_id)
            if alarm is None:
                return None
            alarm.alarm_status = status
            if status == "confirmed":
                alarm.confirmed_by = operator_id
                alarm.confirmed_at = func.now()
            if status in {"processing", "closed", "false_alarm"}:
                alarm.processed_by = operator_id
                alarm.processed_at = func.now()
            if close_alarm:
                alarm.closed_time = func.now()
            session.flush()
            session.refresh(alarm)
            return model_to_dict(alarm)

    def list_process_logs(self, alarm_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            logs = session.scalars(
                select(AlarmProcessLog)
                .where(AlarmProcessLog.alarm_id == alarm_id)
                .order_by(AlarmProcessLog.log_id)
            ).all()
            return [model_to_dict(log) for log in logs]

    def add_process_log(self, alarm_id: int, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            log = AlarmProcessLog(
                alarm_id=alarm_id,
                handler_id=data.get("handler_id"),
                action_type=data["action_type"],
                process_desc=data.get("process_desc"),
                process_result=data.get("process_result", "success"),
            )
            flush_refresh(session, log)
            return model_to_dict(log)
