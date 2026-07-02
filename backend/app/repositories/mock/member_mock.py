from app.repositories.entities import MemberEntity
from app.repositories.mock.store import store
from app.utils.time import now_str


class MockMemberRepository:
    def list_by_home(self, home_id: int) -> list[MemberEntity]:
        return [m for m in store.members.values() if m.home_id == home_id and m.status != "REMOVED"]

    def find_by_id(self, member_id: int) -> MemberEntity | None:
        return store.members.get(member_id)

    def find_active(self, home_id: int, user_id: int) -> MemberEntity | None:
        return next((m for m in store.members.values() if m.home_id == home_id and m.user_id == user_id and m.status == "ACTIVE"), None)

    def find_by_home_and_user(self, home_id: int, user_id: int) -> MemberEntity | None:
        return next((m for m in store.members.values() if m.home_id == home_id and m.user_id == user_id and m.status != "REMOVED"), None)

    def find_by_home_and_phone(self, home_id: int, phone: str) -> MemberEntity | None:
        return next((m for m in store.members.values() if m.home_id == home_id and m.phone == phone and m.status != "REMOVED"), None)

    def invite(self, home_id: int, user_id: int, username: str, phone: str, role: str, expire_at: str | None, invited_by: int) -> MemberEntity:
        member = MemberEntity(store.member_seq, home_id, user_id, username, phone, role, "INVITED", expire_at, invited_by, None, now_str())
        store.members[member.member_id] = member
        store.member_seq += 1
        return member

    def accept_invitation(self, member_id: int, user_id: int, username: str, phone: str) -> MemberEntity | None:
        member = store.members.get(member_id)
        if not member or member.status != "INVITED" or member.phone != phone:
            return None
        member.user_id = user_id
        member.username = username
        member.status = "ACTIVE"
        return member

    def apply(self, home_id: int, user_id: int, username: str, phone: str, reason: str | None) -> MemberEntity:
        member = MemberEntity(store.member_seq, home_id, user_id, username, phone, "MEMBER", "PENDING", None, None, reason, now_str())
        store.members[member.member_id] = member
        store.member_seq += 1
        return member

    def approve(self, member_id: int, approved: bool, role: str) -> MemberEntity | None:
        member = store.members.get(member_id)
        if not member or member.status not in {"PENDING", "INVITED"}:
            return None
        member.status = "ACTIVE" if approved else "REJECTED"
        member.role = role
        return member

    def update_permission(self, member_id: int, role: str, expire_at: str | None) -> MemberEntity | None:
        member = store.members.get(member_id)
        if not member or member.status != "ACTIVE":
            return None
        member.role = role
        member.expire_at = expire_at
        return member

    def remove(self, member_id: int) -> bool:
        member = store.members.get(member_id)
        if not member:
            return False
        member.status = "REMOVED"
        return True