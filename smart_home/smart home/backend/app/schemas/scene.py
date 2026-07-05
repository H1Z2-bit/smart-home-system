from typing import Any

from pydantic import BaseModel, Field


class SceneAction(BaseModel):
    device_id: int = Field(..., gt=0, description="目标设备编号")
    target_state: str = Field(..., min_length=1, max_length=50, description="目标状态")
    param_value: Any | None = Field(default=None, description="可选参数")
    sort_no: int = Field(default=1, ge=1, description="执行顺序")


class SceneCreate(BaseModel):
    scene_name: str = Field(..., min_length=1, max_length=100, description="情景名称")
    enabled: bool = Field(default=True, description="是否启用")
    actions: list[SceneAction] = Field(default_factory=list, description="情景动作")


class SceneUpdate(BaseModel):
    scene_name: str | None = Field(default=None, min_length=1, max_length=100, description="情景名称")
    enabled: bool | None = Field(default=None, description="是否启用")
    actions: list[SceneAction] | None = Field(default=None, description="情景动作")


class SceneOut(BaseModel):
    scene_id: int
    home_id: int
    scene_name: str
    enabled: bool
    actions: list[SceneAction]
    created_at: str
