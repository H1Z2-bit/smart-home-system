from sqlalchemy import desc, select

from app.models.operation_log import AccountOperationLog
from app.repositories.entities import AccountOperationLogEntity
from app.repositories.mysql.base import flush_refresh, session_scope


class MySQLAccountOperationLogRepository:
    def write(self, user_id: int, home_id: int | None, action: str, description: str, target_type: str | None, target_id: int | None) -> AccountOperationLogEntity:
        with session_scope() as session:
            log = AccountOperationLog(
                user_id=user_id,
                home_id=home_id,
                action=action,
                description=description,
                target_type=target_type,
                target_id=target_id,
            )
            flush_refresh(session, log)
            return self._to_entity(log)

    def list_by_home(self, home_id: int, limit: int = 100) -> list[AccountOperationLogEntity]:
        with session_scope() as session:
            logs = session.scalars(
                select(AccountOperationLog)
                .where((AccountOperationLog.home_id == home_id) | (AccountOperationLog.home_id.is_(None)))
                .order_by(desc(AccountOperationLog.created_at), desc(AccountOperationLog.log_id))
                .limit(limit)
            ).all()
            return [self._to_entity(log) for log in logs]

    @staticmethod
    def _to_entity(log: AccountOperationLog) -> AccountOperationLogEntity:
        return AccountOperationLogEntity(
            log_id=log.log_id,
            user_id=log.user_id or 0,
            home_id=log.home_id,
            action=log.action,
            description=log.description,
            target_type=log.target_type,
            target_id=log.target_id,
            created_at=str(log.created_at),
        )
