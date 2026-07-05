from typing import Any

from sqlalchemy import select

from app.models.telemetry import SelfCheckRecord
from app.repositories.mysql.base import flush_refresh, model_to_dict, session_scope
from app.repositories.self_check_repository import SelfCheckRepository


class MySQLSelfCheckRepository(SelfCheckRepository):
    def list_by_device(self, device_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            records = session.scalars(
                select(SelfCheckRecord)
                .where(SelfCheckRecord.device_id == device_id)
                .order_by(SelfCheckRecord.check_id.desc())
            ).all()
            return [model_to_dict(record) for record in records]

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            record = SelfCheckRecord(
                device_id=data["device_id"],
                check_type=data.get("check_type", "manual"),
                check_result=data["check_result"],
                error_info=data.get("error_info"),
                operator_id=data.get("operator_id", 1),
                check_items=data.get("check_items"),
                duration_ms=data.get("duration_ms"),
            )
            flush_refresh(session, record)
            return model_to_dict(record)

