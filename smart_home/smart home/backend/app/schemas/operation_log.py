from pydantic import BaseModel, Field


class OperationLogOut(BaseModel):
    log_id: int = Field(..., description="日志编号")
    home_id: int = Field(..., description="家庭空间编号")
    operator_id: int = Field(..., description="操作人编号")
    operation_type: str = Field(..., description="操作类型")
    operation_object: str = Field(..., description="操作对象")
    operation_result: str = Field(..., description="操作结果")
    operation_desc: str | None = Field(default=None, description="操作说明")
    created_at: str = Field(..., description="创建时间")
