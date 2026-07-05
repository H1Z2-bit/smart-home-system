from abc import ABC, abstractmethod
from typing import Any


class AlarmRepository(ABC):
    @abstractmethod
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get(self, alarm_id: int) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update_status(
        self,
        alarm_id: int,
        status: str,
        operator_id: int | None = None,
        close_alarm: bool = False,
    ) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def list_process_logs(self, alarm_id: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def add_process_log(self, alarm_id: int, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
