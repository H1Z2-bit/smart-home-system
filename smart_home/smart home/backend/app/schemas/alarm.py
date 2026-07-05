from pydantic import BaseModel, Field


class AlarmProcessRequest(BaseModel):
    process_desc: str | None = Field(default=None, max_length=500, description="处理说明")
    process_result: str | None = Field(default="success", max_length=100, description="处理结果")
