from typing import Any

from sqlalchemy import desc, select

from app.models.operation_log import OperationLog
from app.repositories.mysql.base import flush_refresh, model_to_dict, session_scope
from app.repositories.operation_log_repository import OperationLogRepository


class MySQLOperationLogRepository(OperationLogRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            logs = session.scalars(
                select(OperationLog)
                .where(OperationLog.home_id == home_id)
                .order_by(desc(OperationLog.created_at), desc(OperationLog.log_id))
            ).all()
            return [model_to_dict(log) for log in logs]

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            log = OperationLog(
                home_id=data["home_id"],
                operator_id=data["operator_id"],
                operation_type=data["operation_type"],
                operation_object=data["operation_object"],
                operation_result=data["operation_result"],
                operation_desc=data.get("operation_desc"),
            )
            flush_refresh(session, log)
            return model_to_dict(log)

