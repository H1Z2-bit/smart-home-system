from app.repositories.entities import UserEntity
from app.repositories.mock.account_store import store


class MockUserRepository:
    def find_by_phone(self, phone: str) -> UserEntity | None:
        return next((user for user in store.users.values() if user.phone == phone), None)

    def find_by_verified_phone(self, phone: str) -> UserEntity | None:
        return next(
            (user for user in store.users.values() if user.phone == phone and user.phone_verified),
            None,
        )

    def find_by_username(self, username: str) -> UserEntity | None:
        return next((user for user in store.users.values() if user.username == username), None)

    def find_by_id(self, user_id: int) -> UserEntity | None:
        return store.users.get(user_id)

    def save(
        self,
        username: str,
        phone: str,
        password_hash: str,
        role: str = "MEMBER",
        phone_verified: bool = False,
    ) -> UserEntity:
        user = UserEntity(store.user_seq, username, phone, password_hash, role, phone_verified=phone_verified)
        store.users[user.user_id] = user
        store.user_seq += 1
        return user

    def update_password(self, user_id: int, new_password_hash: str) -> None:
        user = store.users[user_id]
        user.password_hash = new_password_hash

    def verify_phone(self, user_id: int) -> UserEntity:
        user = store.users[user_id]
        user.phone_verified = True
        return user

    def bind_phone(self, user_id: int, phone: str) -> UserEntity:
        user = store.users[user_id]
        user.phone = phone
        user.phone_verified = True
        return user
