from typing import Any

from sqlalchemy import select

from app.models.automation import ScheduleTask
from app.repositories.mysql.base import flush_refresh, model_to_dict, parse_datetime, session_scope
from app.repositories.schedule_repository import ScheduleRepository


class MySQLScheduleRepository(ScheduleRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            tasks = session.scalars(select(ScheduleTask).where(ScheduleTask.home_id == home_id).order_by(ScheduleTask.task_id)).all()
            return [model_to_dict(task) for task in tasks]

    def get(self, task_id: int) -> dict[str, Any] | None:
        with session_scope() as session:
            task = session.get(ScheduleTask, task_id)
            return model_to_dict(task) if task else None

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            task = ScheduleTask(
                home_id=home_id,
                device_id=data["device_id"],
                task_name=data["task_name"],
                schedule_type=data.get("schedule_type", "once"),
                execute_time=parse_datetime(data["execute_time"]),
                cron_expr=data.get("cron_expr"),
                action=data["action"],
                status=data.get("status", "enabled"),
                next_run_at=parse_datetime(data.get("execute_time")),
            )
            flush_refresh(session, task)
            return model_to_dict(task)

    def update(self, task_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        with session_scope() as session:
            task = session.get(ScheduleTask, task_id)
            if task is None:
                return None
            for key in ["device_id", "task_name", "action", "status", "schedule_type", "cron_expr"]:
                if key in data and data[key] is not None:
                    setattr(task, key, data[key])
            if "execute_time" in data and data["execute_time"] is not None:
                task.execute_time = parse_datetime(data["execute_time"])
                task.next_run_at = parse_datetime(data["execute_time"])
            session.flush()
            session.refresh(task)
            return model_to_dict(task)

    def delete(self, task_id: int) -> bool:
        with session_scope() as session:
            task = session.get(ScheduleTask, task_id)
            if task is None:
                return False
            session.delete(task)
            return True

