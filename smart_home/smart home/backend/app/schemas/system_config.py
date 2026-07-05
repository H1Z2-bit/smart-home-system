from pydantic import BaseModel


class SystemConfigUpdateRequest(BaseModel):
    alarm_smoke_threshold: float | None = None
    alarm_gas_threshold: float | None = None
    temperature_high_threshold: float | None = None
    auto_alarm_enabled: bool | None = None
    simulation_enabled: bool | None = None


class SystemConfigInfo(BaseModel):
    home_id: int
    alarm_smoke_threshold: float
    alarm_gas_threshold: float
    temperature_high_threshold: float
    auto_alarm_enabled: bool
    simulation_enabled: bool