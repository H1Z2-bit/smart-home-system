from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    device_id: int = Field(..., gt=0, description="目标设备编号")
    task_name: str = Field(..., min_length=1, max_length=100, description="任务名称")
    execute_time: str = Field(..., min_length=1, description="执行时间")
    action: str = Field(..., min_length=1, max_length=100, description="执行动作")
    status: str = Field(default="enabled", max_length=20, description="任务状态")


class ScheduleUpdate(BaseModel):
    device_id: int | None = Field(default=None, gt=0, description="目标设备编号")
    task_name: str | None = Field(default=None, min_length=1, max_length=100, description="任务名称")
    execute_time: str | None = Field(default=None, min_length=1, description="执行时间")
    action: str | None = Field(default=None, min_length=1, max_length=100, description="执行动作")
    status: str | None = Field(default=None, max_length=20, description="任务状态")


class ScheduleStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=20, description="enabled 或 disabled")
