from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class RoomArea(Base):
    __tablename__ = "room_area"

    room_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    room_name: Mapped[str] = mapped_column(String(100), nullable=False)
    room_type: Mapped[str | None] = mapped_column(String(50))
    remark: Mapped[str | None] = mapped_column(String(255))
    sort_no: Mapped[int] = mapped_column(nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())


class RoomLayout(Base):
    __tablename__ = "room_layout"

    layout_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("room_area.room_id", ondelete="CASCADE"), nullable=False)
    position_x: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    position_y: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    width: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=4)
    height: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=3)
    floor_no: Mapped[int] = mapped_column(nullable=False, default=1)
    wall_color: Mapped[str | None] = mapped_column(String(30))
    floor_color: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())


class Device(Base):
    __tablename__ = "device"

    device_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("room_area.room_id"), nullable=False)
    device_name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    device_status: Mapped[str] = mapped_column(String(30), nullable=False, default="offline")
    is_key_device: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    manufacturer: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    serial_no: Mapped[str | None] = mapped_column(String(100), unique=True)
    last_online_at: Mapped[object | None] = mapped_column(DateTime)
    last_offline_at: Mapped[object | None] = mapped_column(DateTime)
    remark: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())


class DeviceLayout(Base):
    __tablename__ = "device_layout"

    layout_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("device.device_id", ondelete="CASCADE"), nullable=False)
    position_x: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    position_y: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    position_z: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    rotation_x: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    rotation_y: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    rotation_z: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    icon_name: Mapped[str | None] = mapped_column(String(80))
    model_name: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())


class DeviceEvent(Base):
    __tablename__ = "device_event"

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("device.device_id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(30))
    new_status: Mapped[str | None] = mapped_column(String(30))
    event_desc: Mapped[str | None] = mapped_column(String(500))
    operator_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_account.user_id", ondelete="SET NULL"))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())

