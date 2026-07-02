from pydantic import BaseModel


class OperationLogInfo(BaseModel):
    log_id: int
    user_id: int
    home_id: int | None
    action: str
    description: str
    target_type: str | None
    target_id: int | None
    created_at: str