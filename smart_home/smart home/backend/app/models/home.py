from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class HomeSpace(Base):
    __tablename__ = "home_space"

    home_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_account.user_id"), nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())


class HomeMember(Base):
    __tablename__ = "home_member"

    member_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_account.user_id", ondelete="SET NULL"))
    username: Mapped[str | None] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="INVITED")
    expire_at: Mapped[object | None] = mapped_column(DateTime)
    invited_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_account.user_id", ondelete="SET NULL"))
    apply_reason: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[object | None] = mapped_column(DateTime, onupdate=func.now())
