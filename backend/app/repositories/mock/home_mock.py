from app.repositories.entities import HomeEntity, MemberEntity
from app.repositories.mock.store import store
from app.utils.time import now_str


class MockHomeRepository:
    def create(self, owner_id: int, owner_username: str, owner_phone: str, name: str, address: str | None) -> HomeEntity:
        home = HomeEntity(store.home_seq, name, address, owner_id, now_str())
        store.homes[home.home_id] = home
        member = MemberEntity(store.member_seq, home.home_id, owner_id, owner_username, owner_phone, "OWNER", "ACTIVE")
        store.members[member.member_id] = member
        store.home_seq += 1
        store.member_seq += 1
        return home

    def list_by_user(self, user_id: int) -> list[HomeEntity]:
        home_ids = {m.home_id for m in store.members.values() if m.user_id == user_id and m.status == "ACTIVE"}
        return [home for home in store.homes.values() if home.home_id in home_ids]

    def find_by_id(self, home_id: int) -> HomeEntity | None:
        return store.homes.get(home_id)

    def update(self, home_id: int, name: str | None, address: str | None) -> HomeEntity | None:
        home = store.homes.get(home_id)
        if not home:
            return None
        if name is not None:
            home.name = name
        if address is not None:
            home.address = address
        return home

    def delete(self, home_id: int) -> bool:
        if home_id not in store.homes:
            return False
        del store.homes[home_id]
        return True