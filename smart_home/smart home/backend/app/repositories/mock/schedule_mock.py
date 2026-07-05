from typing import Any

from app.repositories.mock import store
from app.repositories.schedule_repository import ScheduleRepository


class MockScheduleRepository(ScheduleRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        return [store.copy_record(task) for task in store.schedules.values() if task["home_id"] == home_id]

    def get(self, task_id: int) -> dict[str, Any] | None:
        return store.copy_record(store.schedules.get(task_id))

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        task_id = store.next_schedule_id()
        task = {
            "task_id": task_id,
            "home_id": home_id,
            "device_id": data["device_id"],
            "task_name": data["task_name"],
            "execute_time": data["execute_time"],
            "action": data["action"],
            "status": data.get("status", "enabled"),
            "created_at": store.now_text(),
        }
        store.schedules[task_id] = task
        return store.copy_record(task)

    def update(self, task_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        task = store.schedules.get(task_id)
        if task is None:
            return None
        for key in ["device_id", "task_name", "execute_time", "action", "status"]:
            if key in data and data[key] is not None:
                task[key] = data[key]
        return store.copy_record(task)

    def delete(self, task_id: int) -> bool:
        if task_id not in store.schedules:
            return False
        del store.schedules[task_id]
        return True
