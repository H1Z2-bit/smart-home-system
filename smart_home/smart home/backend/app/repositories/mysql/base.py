from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


class MySQLRepositoryNotReady(RuntimeError):
    """Raised when a reserved MySQL repository is called before implementation."""


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def model_to_dict(model: Any, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {
        column.name: normalize_value(getattr(model, column.name))
        for column in model.__table__.columns
    }
    if extra:
        result.update(extra)
    return result


def normalize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, Decimal):
        return float(value)
    return value


def flush_refresh(session: Session, model: Any) -> Any:
    session.add(model)
    session.flush()
    session.refresh(model)
    return model


def parse_datetime(value: Any) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return datetime.fromisoformat(text)


def mysql_not_ready(repository_name: str, method_name: str) -> None:
    raise MySQLRepositoryNotReady(
        f"{repository_name}.{method_name} is reserved for SQLAlchemy/MySQL implementation."
    )
