from dataclasses import dataclass


@dataclass
class UserEntity:
    user_id: int
    username: str
    phone: str
    password_hash: str
    role: str
    status: str = "ACTIVE"


@dataclass
class HomeEntity:
    home_id: int
    name: str
    address: str | None
    owner_id: int
    created_at: str


@dataclass
class MemberEntity:
    member_id: int
    home_id: int
    user_id: int
    username: str
    phone: str
    role: str
    status: str
    expire_at: str | None = None
    invited_by: int | None = None
    apply_reason: str | None = None
    created_at: str | None = None


@dataclass
class SystemConfigEntity:
    home_id: int
    alarm_smoke_threshold: float = 80.0
    alarm_gas_threshold: float = 70.0
    temperature_high_threshold: float = 35.0
    auto_alarm_enabled: bool = True
    simulation_enabled: bool = True


@dataclass
class OperationLogEntity:
    log_id: int
    user_id: int
    home_id: int | None
    action: str
    description: str
    target_type: str | None
    target_id: int | None
    created_at: str