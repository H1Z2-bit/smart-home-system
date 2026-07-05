from typing import Any

from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    room_id: int = Field(..., gt=0, description="所属房间编号")
    device_name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    device_type: str = Field(..., min_length=1, max_length=50, description="设备类型")
    device_status: str | None = Field(default="offline", max_length=30, description="设备状态")
    is_key_device: bool = Field(default=False, description="是否关键安全设备")


class DeviceCreateCompat(DeviceCreate):
    home_id: int = Field(..., gt=0, description="家庭空间编号")


class DeviceUpdate(BaseModel):
    room_id: int | None = Field(default=None, gt=0, description="所属房间编号")
    device_name: str | None = Field(default=None, min_length=1, max_length=100, description="设备名称")
    device_type: str | None = Field(default=None, min_length=1, max_length=50, description="设备类型")
    device_status: str | None = Field(default=None, max_length=30, description="设备状态")
    is_key_device: bool | None = Field(default=None, description="是否关键安全设备")


class DeviceControl(BaseModel):
    action: str = Field(..., min_length=1, max_length=50, description="控制动作，如 switch")
    target_state: str = Field(..., min_length=1, max_length=30, description="目标状态，如 on/off")
    param_value: Any | None = Field(default=None, description="可选控制参数，如亮度、功率等")


class DeviceOut(BaseModel):
    device_id: int
    home_id: int
    room_id: int
    device_name: str
    device_type: str
    device_status: str
    is_key_device: bool
    created_at: str
