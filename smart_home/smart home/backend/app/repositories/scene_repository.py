from abc import ABC, abstractmethod
from typing import Any


class SceneRepository(ABC):
    @abstractmethod
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get(self, scene_id: int) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def exists_name(self, home_id: int, scene_name: str, exclude_scene_id: int | None = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update(self, scene_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, scene_id: int) -> bool:
        raise NotImplementedError
