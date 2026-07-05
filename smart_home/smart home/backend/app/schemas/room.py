from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    room_name: str = Field(..., min_length=1, max_length=100, description="房间名称")
    room_type: str | None = Field(default=None, max_length=50, description="房间类型")
    remark: str | None = Field(default=None, max_length=255, description="备注")


class RoomCreateCompat(RoomCreate):
    home_id: int = Field(..., gt=0, description="家庭空间编号")


class RoomUpdate(BaseModel):
    room_name: str = Field(..., min_length=1, max_length=100, description="房间名称")
    room_type: str | None = Field(default=None, max_length=50, description="房间类型")
    remark: str | None = Field(default=None, max_length=255, description="备注")


class RoomOut(BaseModel):
    room_id: int
    home_id: int
    room_name: str
    room_type: str | None = None
    remark: str | None = None
