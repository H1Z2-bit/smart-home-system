from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class AlarmRecord(Base):
    __tablename__ = "alarm_record"

    alarm_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("device.device_id", ondelete="CASCADE"), nullable=False)
    alarm_type: Mapped[str] = mapped_column(String(50), nullable=False)
    alarm_level: Mapped[str] = mapped_column(String(20), nullable=False)
    trigger_value: Mapped[str] = mapped_column(String(100), nullable=False)
    alarm_status: Mapped[str] = mapped_column(String(20), nullable=False, default="new")
    alarm_desc: Mapped[str | None] = mapped_column(String(500))
    confirmed_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_account.user_id", ondelete="SET NULL"))
    confirmed_at: Mapped[object | None] = mapped_column(DateTime)
    processed_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_account.user_id", ondelete="SET NULL"))
    processed_at: Mapped[object | None] = mapped_column(DateTime)
    trigger_time: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    closed_time: Mapped[object | None] = mapped_column(DateTime)


class AlarmProcessLog(Base):
    __tablename__ = "alarm_process_log"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    alarm_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("alarm_record.alarm_id", ondelete="CASCADE"), nullable=False)
    handler_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_account.user_id", ondelete="SET NULL"))
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    process_desc: Mapped[str | None] = mapped_column(String(500))
    process_result: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())

