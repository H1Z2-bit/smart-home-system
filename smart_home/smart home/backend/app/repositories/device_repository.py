from abc import ABC, abstractmethod
from typing import Any


class DeviceRepository(ABC):
    @abstractmethod
    def list_by_home(self, home_id: int, room_id: int | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get(self, device_id: int) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def exists_name(self, room_id: int, device_name: str, exclude_device_id: int | None = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def count_by_room(self, room_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update(self, device_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, device_id: int, device_status: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, device_id: int) -> bool:
        raise NotImplementedError
