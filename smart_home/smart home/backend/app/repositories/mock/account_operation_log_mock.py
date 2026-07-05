from app.repositories.entities import AccountOperationLogEntity
from app.repositories.mock.account_store import store
from app.utils.time import now_str


class MockAccountOperationLogRepository:
    def write(
        self,
        user_id: int,
        home_id: int | None,
        action: str,
        description: str,
        target_type: str | None = None,
        target_id: int | None = None,
    ) -> AccountOperationLogEntity:
        log = AccountOperationLogEntity(
            store.log_seq,
            user_id,
            home_id,
            action,
            description,
            target_type,
            target_id,
            now_str(),
        )
        store.logs.insert(0, log)
        store.log_seq += 1
        return log

    def list_by_home(self, home_id: int, limit: int = 100) -> list[AccountOperationLogEntity]:
        return [log for log in store.logs if log.home_id in (home_id, None)][:limit]
