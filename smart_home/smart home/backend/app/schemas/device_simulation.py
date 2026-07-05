from typing import Any, Literal

from pydantic import BaseModel, Field


class DeviceSimulationCreate(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=100, description="模拟指标名称")
    metric_value: Any = Field(..., description="模拟指标值")
    device_status: str | None = Field(default=None, max_length=30, description="可选设备状态")
    trigger_alarm: bool = Field(default=False, description="是否触发报警")
    alarm_type: str | None = Field(default=None, max_length=50, description="报警类型")
    alarm_level: str = Field(default="warning", max_length=30, description="报警级别")
    simulation_type: Literal["manual", "auto", "scenario"] = Field(default="manual", description="模拟类型")
    scenario_name: str | None = Field(default=None, max_length=100, description="模拟场景名称")
