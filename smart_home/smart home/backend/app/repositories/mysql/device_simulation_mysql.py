from typing import Any

from sqlalchemy import select

from app.models.telemetry import DeviceSimulation
from app.repositories.device_simulation_repository import DeviceSimulationRepository
from app.repositories.mysql.base import flush_refresh, model_to_dict, session_scope


class MySQLDeviceSimulationRepository(DeviceSimulationRepository):
    def list_by_device(self, device_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            records = session.scalars(
                select(DeviceSimulation)
                .where(DeviceSimulation.device_id == device_id)
                .order_by(DeviceSimulation.simulation_id.desc())
            ).all()
            return [model_to_dict(record) for record in records]

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            record = DeviceSimulation(
                home_id=data["home_id"],
                device_id=data["device_id"],
                metric_name=data["metric_name"],
                metric_value=str(data["metric_value"]),
                device_status=data.get("device_status"),
                trigger_alarm=bool(data.get("trigger_alarm", False)),
                alarm_type=data.get("alarm_type"),
                alarm_level=data.get("alarm_level", "warning"),
                alarm_id=data.get("alarm_id"),
                simulation_type=data.get("simulation_type", "manual"),
                scenario_name=data.get("scenario_name"),
            )
            flush_refresh(session, record)
            return model_to_dict(record)

