from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class SceneMode(Base):
    __tablename__ = "scene_mode"

    scene_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    scene_name: Mapped[str] = mapped_column(String(100), nullable=False)
    scene_desc: Mapped[str | None] = mapped_column(String(255))
    icon_name: Mapped[str | None] = mapped_column(String(80))
    sort_no: Mapped[int] = mapped_column(nullable=False, default=1)
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_account.user_id"), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())


class SceneDeviceAction(Base):
    __tablename__ = "scene_device_action"

    action_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    scene_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("scene_mode.scene_id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("device.device_id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False, default="switch")
    target_state: Mapped[str] = mapped_column(String(50), nullable=False)
    param_value: Mapped[str | None] = mapped_column(String(100))
    sort_no: Mapped[int] = mapped_column(nullable=False, default=1)


class ScheduleTask(Base):
    __tablename__ = "schedule_task"

    task_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("device.device_id", ondelete="CASCADE"), nullable=False)
    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(20), nullable=False, default="once")
    execute_time: Mapped[object] = mapped_column(DateTime, nullable=False)
    cron_expr: Mapped[str | None] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="enabled")
    last_run_at: Mapped[object | None] = mapped_column(DateTime)
    next_run_at: Mapped[object | None] = mapped_column(DateTime)
    run_count: Mapped[int] = mapped_column(nullable=False, default=0)
    fail_reason: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())


class LinkageRule(Base):
    __tablename__ = "linkage_rule"

    rule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger_condition: Mapped[dict] = mapped_column(JSON, nullable=False)
    action_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_account.user_id"), nullable=False)
    last_triggered_at: Mapped[object | None] = mapped_column(DateTime)
    trigger_count: Mapped[int] = mapped_column(nullable=False, default=0)
    rule_desc: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())

