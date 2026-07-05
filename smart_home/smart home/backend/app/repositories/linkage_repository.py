from abc import ABC, abstractmethod
from typing import Any


class LinkageRepository(ABC):
    @abstractmethod
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get(self, rule_id: int) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update(self, rule_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, rule_id: int) -> bool:
        raise NotImplementedError
