from sqlalchemy import BigInteger, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    config_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id"), nullable=False)
    alarm_smoke_threshold: Mapped[float] = mapped_column(Float, default=80.0)
    alarm_gas_threshold: Mapped[float] = mapped_column(Float, default=70.0)
    temperature_high_threshold: Mapped[float] = mapped_column(Float, default=35.0)
    auto_alarm_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    simulation_enabled: Mapped[bool] = mapped_column(Boolean, default=True)