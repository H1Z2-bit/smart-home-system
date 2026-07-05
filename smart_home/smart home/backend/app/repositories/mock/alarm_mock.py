from typing import Any

from app.repositories.alarm_repository import AlarmRepository
from app.repositories.mock import store


class MockAlarmRepository(AlarmRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        return [store.copy_record(alarm) for alarm in store.alarms.values() if alarm["home_id"] == home_id]

    def get(self, alarm_id: int) -> dict[str, Any] | None:
        return store.copy_record(store.alarms.get(alarm_id))

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        alarm_id = store.next_alarm_id()
        alarm = {
            "alarm_id": alarm_id,
            "home_id": data["home_id"],
            "device_id": data["device_id"],
            "alarm_type": data["alarm_type"],
            "alarm_level": data.get("alarm_level", "warning"),
            "trigger_value": data.get("trigger_value"),
            "alarm_status": data.get("alarm_status", "new"),
            "trigger_time": store.now_text(),
            "closed_time": None,
        }
        store.alarms[alarm_id] = alarm
        self.add_process_log(
            alarm_id,
            {
                "handler_id": None,
                "action_type": "notify",
                "process_desc": data.get("process_desc", "设备模拟触发报警"),
                "process_result": "success",
            },
        )
        return store.copy_record(alarm)

    def update_status(
        self,
        alarm_id: int,
        status: str,
        operator_id: int | None = None,
        close_alarm: bool = False,
    ) -> dict[str, Any] | None:
        alarm = store.alarms.get(alarm_id)
        if alarm is None:
            return None
        alarm["alarm_status"] = status
        if status == "confirmed":
            alarm["confirmed_by"] = operator_id
            alarm["confirmed_at"] = store.now_text()
        if status in {"processing", "closed", "false_alarm"}:
            alarm["processed_by"] = operator_id
            alarm["processed_at"] = store.now_text()
        if close_alarm:
            alarm["closed_time"] = store.now_text()
        return store.copy_record(alarm)

    def list_process_logs(self, alarm_id: int) -> list[dict[str, Any]]:
        return [store.copy_record(log) for log in store.alarm_process_logs if log["alarm_id"] == alarm_id]

    def add_process_log(self, alarm_id: int, data: dict[str, Any]) -> dict[str, Any]:
        log = {
            "log_id": store.next_alarm_process_log_id(),
            "alarm_id": alarm_id,
            "handler_id": data.get("handler_id"),
            "action_type": data["action_type"],
            "process_desc": data.get("process_desc"),
            "process_result": data.get("process_result", "success"),
            "created_at": store.now_text(),
        }
        store.alarm_process_logs.append(log)
        return store.copy_record(log)
