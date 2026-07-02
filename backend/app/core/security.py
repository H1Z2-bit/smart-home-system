from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


@dataclass
class TokenPayload:
    user_id: int
    username: str
    role: str


def _password_bytes(password: str) -> bytes:
    # bcrypt has a 72-byte input limit. Hashing first keeps Unicode passwords safe.
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(_password_bytes(password), password_hash.encode("utf-8"))


def _read_key(path: str) -> str | None:
    key_path = Path(path)
    if key_path.exists():
        return key_path.read_text(encoding="utf-8")
    return None


def _signing_key() -> tuple[str, str]:
    private_key = _read_key(settings.jwt_private_key_path)
    if private_key:
        return private_key, settings.jwt_algorithm
    return settings.jwt_mock_secret, "HS256"


def _verify_key() -> tuple[str, str]:
    public_key = _read_key(settings.jwt_public_key_path)
    if public_key:
        return public_key, settings.jwt_algorithm
    return settings.jwt_mock_secret, "HS256"


def create_access_token(user_id: int, username: str, role: str) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire_at,
    }
    key, algorithm = _signing_key()
    return jwt.encode(payload, key, algorithm=algorithm)


def parse_access_token(token: str) -> TokenPayload | None:
    key, algorithm = _verify_key()
    try:
        payload = jwt.decode(token, key, algorithms=[algorithm])
        return TokenPayload(
            user_id=int(payload.get("sub")),
            username=str(payload.get("username")),
            role=str(payload.get("role")),
        )
    except (JWTError, TypeError, ValueError):
        return None