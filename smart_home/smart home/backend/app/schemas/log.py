from pydantic import BaseModel


class OperationLogInfo(BaseModel):
    log_id: int
    home_id: int | None
    operator_id: int
    operation_type: str
    operation_object: str
    operation_result: str
    operation_desc: str | None
    created_at: str


class AccountOperationLogInfo(BaseModel):
    log_id: int
    user_id: int | None
    home_id: int | None
    action: str
    description: str
    target_type: str | None
    target_id: int | None
    created_at: str
