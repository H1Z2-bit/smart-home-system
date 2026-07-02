from app.repositories.entities import UserEntity
from app.repositories.mock.store import store


class MockUserRepository:
    def find_by_phone(self, phone: str) -> UserEntity | None:
        return next((user for user in store.users.values() if user.phone == phone), None)

    def find_by_id(self, user_id: int) -> UserEntity | None:
        return store.users.get(user_id)

    def save(self, username: str, phone: str, password_hash: str, role: str = "MEMBER") -> UserEntity:
        user = UserEntity(store.user_seq, username, phone, password_hash, role)
        store.users[user.user_id] = user
        store.user_seq += 1
        return user

    def update_password(self, user_id: int, new_password_hash: str) -> None:
        user = store.users[user_id]
        user.password_hash = new_password_hash