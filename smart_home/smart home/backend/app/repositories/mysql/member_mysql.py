from sqlalchemy import select

from app.models.home import HomeMember
from app.repositories.entities import MemberEntity
from app.repositories.mysql.base import flush_refresh, parse_datetime, session_scope
from app.repositories.mysql.home_mysql import member_to_entity


class MySQLMemberRepository:
    def list_by_home(self, home_id: int) -> list[MemberEntity]:
        with session_scope() as session:
            members = session.scalars(
                select(HomeMember)
                .where(HomeMember.home_id == home_id, HomeMember.status != "REMOVED")
                .order_by(HomeMember.member_id)
            ).all()
            return [member_to_entity(member) for member in members]

    def find_by_id(self, member_id: int) -> MemberEntity | None:
        with session_scope() as session:
            member = session.get(HomeMember, member_id)
            return member_to_entity(member) if member else None

    def find_active(self, home_id: int, user_id: int) -> MemberEntity | None:
        with session_scope() as session:
            member = session.scalar(
                select(HomeMember).where(
                    HomeMember.home_id == home_id,
                    HomeMember.user_id == user_id,
                    HomeMember.status == "ACTIVE",
                )
            )
            return member_to_entity(member) if member else None

    def find_by_home_and_user(self, home_id: int, user_id: int) -> MemberEntity | None:
        with session_scope() as session:
            member = session.scalar(
                select(HomeMember).where(
                    HomeMember.home_id == home_id,
                    HomeMember.user_id == user_id,
                    HomeMember.status != "REMOVED",
                )
            )
            return member_to_entity(member) if member else None

    def find_by_home_and_phone(self, home_id: int, phone: str) -> MemberEntity | None:
        with session_scope() as session:
            member = session.scalar(
                select(HomeMember).where(
                    HomeMember.home_id == home_id,
                    HomeMember.phone == phone,
                    HomeMember.status != "REMOVED",
                )
            )
            return member_to_entity(member) if member else None

    def invite(self, home_id: int, user_id: int, username: str, phone: str, role: str, expire_at: str | None, invited_by: int) -> MemberEntity:
        with session_scope() as session:
            member = HomeMember(
                home_id=home_id,
                user_id=user_id or None,
                username=username or None,
                phone=phone,
                role=role,
                status="INVITED",
                expire_at=parse_datetime(expire_at),
                invited_by=invited_by,
            )
            flush_refresh(session, member)
            return member_to_entity(member)

    def accept_invitation(self, member_id: int, user_id: int, username: str, phone: str) -> MemberEntity | None:
        with session_scope() as session:
            member = session.get(HomeMember, member_id)
            if not member or member.status != "INVITED" or member.phone != phone:
                return None
            member.user_id = user_id
            member.username = username
            member.status = "ACTIVE"
            session.flush()
            session.refresh(member)
            return member_to_entity(member)

    def apply(self, home_id: int, user_id: int, username: str, phone: str, reason: str | None) -> MemberEntity:
        with session_scope() as session:
            member = HomeMember(
                home_id=home_id,
                user_id=user_id,
                username=username,
                phone=phone,
                role="MEMBER",
                status="PENDING",
                apply_reason=reason,
            )
            flush_refresh(session, member)
            return member_to_entity(member)

    def approve(self, member_id: int, approved: bool, role: str) -> MemberEntity | None:
        with session_scope() as session:
            member = session.get(HomeMember, member_id)
            if not member or member.status not in {"PENDING", "INVITED"}:
                return None
            member.status = "ACTIVE" if approved else "REJECTED"
            member.role = role
            session.flush()
            session.refresh(member)
            return member_to_entity(member)

    def update_permission(self, member_id: int, role: str, expire_at: str | None) -> MemberEntity | None:
        with session_scope() as session:
            member = session.get(HomeMember, member_id)
            if not member or member.status != "ACTIVE":
                return None
            member.role = role
            member.expire_at = parse_datetime(expire_at)
            session.flush()
            session.refresh(member)
            return member_to_entity(member)

    def remove(self, member_id: int) -> bool:
        with session_scope() as session:
            member = session.get(HomeMember, member_id)
            if not member:
                return False
            member.status = "REMOVED"
            return True
