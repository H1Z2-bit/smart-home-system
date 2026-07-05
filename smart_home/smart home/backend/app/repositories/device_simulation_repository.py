from abc import ABC, abstractmethod
from typing import Any


class DeviceSimulationRepository(ABC):
    @abstractmethod
    def list_by_device(self, device_id: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
