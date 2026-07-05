from sqlalchemy import select

from app.models.user import UserAccount
from app.repositories.entities import UserEntity
from app.repositories.mysql.base import flush_refresh, session_scope


class MySQLUserRepository:
    def find_by_phone(self, phone: str) -> UserEntity | None:
        with session_scope() as session:
            user = session.scalar(select(UserAccount).where(UserAccount.phone == phone))
            return self._to_entity(user) if user else None

    def find_by_verified_phone(self, phone: str) -> UserEntity | None:
        with session_scope() as session:
            user = session.scalar(
                select(UserAccount).where(
                    UserAccount.phone == phone,
                    UserAccount.phone_verified.is_(True),
                )
            )
            return self._to_entity(user) if user else None

    def find_by_username(self, username: str) -> UserEntity | None:
        with session_scope() as session:
            user = session.scalar(select(UserAccount).where(UserAccount.username == username))
            return self._to_entity(user) if user else None

    def find_by_id(self, user_id: int) -> UserEntity | None:
        with session_scope() as session:
            user = session.get(UserAccount, user_id)
            return self._to_entity(user) if user else None

    def save(
        self,
        username: str,
        phone: str,
        password_hash: str,
        role: str = "MEMBER",
        phone_verified: bool = False,
    ) -> UserEntity:
        register_type = "sms" if phone_verified else "password"
        with session_scope() as session:
            user = UserAccount(
                username=username,
                phone=phone,
                phone_verified=phone_verified,
                register_type=register_type,
                password_hash=password_hash,
                role=role,
                status="ACTIVE",
            )
            flush_refresh(session, user)
            return self._to_entity(user)

    def update_password(self, user_id: int, new_password_hash: str) -> None:
        with session_scope() as session:
            user = session.get(UserAccount, user_id)
            if user:
                user.password_hash = new_password_hash

    def verify_phone(self, user_id: int) -> UserEntity:
        with session_scope() as session:
            user = session.get(UserAccount, user_id)
            if user is None:
                raise KeyError(user_id)
            user.phone_verified = True
            session.flush()
            session.refresh(user)
            return self._to_entity(user)

    def bind_phone(self, user_id: int, phone: str) -> UserEntity:
        with session_scope() as session:
            user = session.get(UserAccount, user_id)
            if user is None:
                raise KeyError(user_id)
            user.phone = phone
            user.phone_verified = True
            session.flush()
            session.refresh(user)
            return self._to_entity(user)

    @staticmethod
    def _to_entity(user: UserAccount) -> UserEntity:
        return UserEntity(
            user_id=user.user_id,
            username=user.username,
            phone=user.phone or "",
            password_hash=user.password_hash,
            role=user.role,
            status=user.status,
            phone_verified=bool(user.phone_verified),
        )

