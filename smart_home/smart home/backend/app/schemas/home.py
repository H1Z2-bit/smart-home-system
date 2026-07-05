from pydantic import BaseModel, Field


class HomeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    address: str | None = None


class HomeUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    address: str | None = None


class HomeInfo(BaseModel):
    home_id: int
    name: str
    address: str | None = None
    owner_id: int
    created_at: str