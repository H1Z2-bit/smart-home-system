from app.core.permissions import Permission, has_permission
from app.repositories.entities import MemberEntity
from app.repositories.factory import get_member_repository
from app.utils.response import AppException


class PermissionService:
    def __init__(self):
        self.members = get_member_repository()

    def require_home_permission(self, home_id: int, user_id: int, permission: Permission) -> MemberEntity:
        member = self.members.find_active(home_id, user_id)
        if not member:
            raise AppException(403, "not home member")
        if not has_permission(member.role, permission):
            raise AppException(403, "permission denied")
        return member

    def require_home_member(self, home_id: int, user_id: int) -> MemberEntity:
        return self.require_home_permission(home_id, user_id, Permission.HOME_VIEW)

    def require_home_owner(self, home_id: int, user_id: int) -> MemberEntity:
        return self.require_home_permission(home_id, user_id, Permission.HOME_MANAGE)
