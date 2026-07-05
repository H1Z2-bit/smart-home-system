from sqlalchemy import select

from app.models.home import HomeMember, HomeSpace
from app.repositories.entities import HomeEntity, MemberEntity
from app.repositories.mysql.base import flush_refresh, session_scope


class MySQLHomeRepository:
    def create(self, owner_id: int, owner_username: str, owner_phone: str, name: str, address: str | None) -> HomeEntity:
        with session_scope() as session:
            home = HomeSpace(
                name=name,
                address=address,
                owner_id=owner_id,
                status="ACTIVE",
            )
            flush_refresh(session, home)
            member = HomeMember(
                home_id=home.home_id,
                user_id=owner_id,
                username=owner_username,
                phone=owner_phone,
                role="OWNER",
                status="ACTIVE",
            )
            session.add(member)
            session.flush()
            session.refresh(home)
            return self._to_entity(home)

    def list_by_user(self, user_id: int) -> list[HomeEntity]:
        with session_scope() as session:
            homes = session.scalars(
                select(HomeSpace)
                .join(HomeMember, HomeMember.home_id == HomeSpace.home_id)
                .where(
                    HomeMember.user_id == user_id,
                    HomeMember.status == "ACTIVE",
                    HomeSpace.status == "ACTIVE",
                )
                .order_by(HomeSpace.home_id)
            ).all()
            return [self._to_entity(home) for home in homes]

    def find_by_id(self, home_id: int) -> HomeEntity | None:
        with session_scope() as session:
            home = session.get(HomeSpace, home_id)
            return self._to_entity(home) if home else None

    def update(self, home_id: int, name: str | None, address: str | None) -> HomeEntity | None:
        with session_scope() as session:
            home = session.get(HomeSpace, home_id)
            if home is None:
                return None
            if name is not None:
                home.name = name
            if address is not None:
                home.address = address
            session.flush()
            session.refresh(home)
            return self._to_entity(home)

    def delete(self, home_id: int) -> bool:
        with session_scope() as session:
            home = session.get(HomeSpace, home_id)
            if home is None:
                return False
            session.delete(home)
            return True

    @staticmethod
    def _to_entity(home: HomeSpace) -> HomeEntity:
        return HomeEntity(
            home_id=home.home_id,
            name=home.name,
            address=home.address,
            owner_id=home.owner_id,
            created_at=str(home.created_at),
        )


def member_to_entity(member: HomeMember) -> MemberEntity:
    return MemberEntity(
        member_id=member.member_id,
        home_id=member.home_id,
        user_id=member.user_id or 0,
        username=member.username or "",
        phone=member.phone,
        role=member.role,
        status=member.status,
        expire_at=str(member.expire_at) if member.expire_at else None,
        invited_by=member.invited_by,
        apply_reason=member.apply_reason,
        created_at=str(member.created_at) if member.created_at else None,
    )

