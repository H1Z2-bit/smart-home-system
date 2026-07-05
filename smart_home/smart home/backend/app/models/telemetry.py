from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    data_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"))
    room_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("room_area.room_id", ondelete="SET NULL"))
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("device.device_id", ondelete="CASCADE"), nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(20))
    collect_time: Mapped[object] = mapped_column(DateTime, server_default=func.now())


class SelfCheckRecord(Base):
    __tablename__ = "self_check_record"

    check_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("device.device_id", ondelete="CASCADE"), nullable=False)
    check_type: Mapped[str] = mapped_column(String(30), nullable=False, default="manual")
    check_result: Mapped[str] = mapped_column(String(30), nullable=False)
    error_info: Mapped[str | None] = mapped_column(String(500))
    check_time: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    operator_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_account.user_id", ondelete="SET NULL"))
    check_items: Mapped[list | None] = mapped_column(JSON)
    duration_ms: Mapped[int | None] = mapped_column()


class DeviceSimulation(Base):
    __tablename__ = "device_simulation"

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("device.device_id", ondelete="CASCADE"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[str] = mapped_column(String(100), nullable=False)
    device_status: Mapped[str | None] = mapped_column(String(30))
    trigger_alarm: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    alarm_type: Mapped[str | None] = mapped_column(String(50))
    alarm_level: Mapped[str] = mapped_column(String(30), nullable=False, default="warning")
    alarm_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("alarm_record.alarm_id", ondelete="SET NULL"))
    simulation_type: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    scenario_name: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())

