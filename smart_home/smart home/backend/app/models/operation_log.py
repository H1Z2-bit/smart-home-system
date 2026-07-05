from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class OperationLog(Base):
    __tablename__ = "operation_log"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    home_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="SET NULL"))
    operator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user_account.user_id"), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    operation_object: Mapped[str] = mapped_column(String(100), nullable=False)
    operation_result: Mapped[str] = mapped_column(String(50), nullable=False)
    operation_desc: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())


class AccountOperationLog(Base):
    __tablename__ = "account_operation_log"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user_account.user_id", ondelete="SET NULL"))
    home_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("home_space.home_id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(80))
    target_id: Mapped[int | None] = mapped_column(BigInteger)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
