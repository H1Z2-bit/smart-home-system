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
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())


class HomeMember(Base):
    __tablename__ = "home_member"

    member_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("home_space.home_id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_account.user_id"), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")
    expire_at: Mapped[object | None] = mapped_column(DateTime)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())