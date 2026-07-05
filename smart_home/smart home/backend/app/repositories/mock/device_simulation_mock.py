from typing import Any

from app.repositories.device_simulation_repository import DeviceSimulationRepository
from app.repositories.mock import store


class MockDeviceSimulationRepository(DeviceSimulationRepository):
    def list_by_device(self, device_id: int) -> list[dict[str, Any]]:
        return [
            store.copy_record(record)
            for record in sorted(store.device_simulations, key=lambda item: item["simulation_id"], reverse=True)
            if record["device_id"] == device_id
        ]

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        record = {
            "simulation_id": store.next_device_simulation_id(),
            "home_id": data["home_id"],
            "device_id": data["device_id"],
            "metric_name": data["metric_name"],
            "metric_value": data["metric_value"],
            "device_status": data.get("device_status"),
            "trigger_alarm": bool(data.get("trigger_alarm", False)),
            "alarm_type": data.get("alarm_type"),
            "alarm_level": data.get("alarm_level", "warning"),
            "alarm_id": data.get("alarm_id"),
            "simulation_type": data.get("simulation_type", "manual"),
            "scenario_name": data.get("scenario_name"),
            "created_at": store.now_text(),
        }
        store.device_simulations.append(record)
        return store.copy_record(record)
