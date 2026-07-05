from typing import Any

from pydantic import BaseModel, Field


class LinkageCreate(BaseModel):
    rule_name: str = Field(..., min_length=1, max_length=100, description="规则名称")
    trigger_condition: dict[str, Any] = Field(..., description="触发条件")
    action_config: dict[str, Any] = Field(..., description="执行动作配置")
    enabled: bool = Field(default=True, description="是否启用")
    created_by: int = Field(default=1, description="创建人")


class LinkageUpdate(BaseModel):
    rule_name: str | None = Field(default=None, min_length=1, max_length=100, description="规则名称")
    trigger_condition: dict[str, Any] | None = Field(default=None, description="触发条件")
    action_config: dict[str, Any] | None = Field(default=None, description="执行动作配置")
    enabled: bool | None = Field(default=None, description="是否启用")
