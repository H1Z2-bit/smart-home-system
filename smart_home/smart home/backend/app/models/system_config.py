from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    config_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    alarm_smoke_threshold: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=80.0)
    alarm_gas_threshold: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=70.0)
    temperature_high_threshold: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=35.0)
    auto_alarm_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    simulation_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())
