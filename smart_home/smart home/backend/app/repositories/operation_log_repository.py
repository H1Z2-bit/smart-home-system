from abc import ABC, abstractmethod
from typing import Any


class OperationLogRepository(ABC):
    @abstractmethod
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
