from app.core.permissions import Permission
from app.repositories.factory import get_member_repository, get_user_repository
from app.services.account_operation_log_service import AccountOperationLogService
from app.services.permission_service import PermissionService
from app.utils.response import AppException


class MemberService:
    def __init__(self):
        self.members = get_member_repository()
        self.users = get_user_repository()
        self.permissions = PermissionService()
        self.logs = AccountOperationLogService()

    def _require_member_manage(self, home_id: int, user_id: int):
        return self.permissions.require_home_permission(home_id, user_id, Permission.MEMBER_MANAGE)

    def invite(self, home_id: int, operator_id: int, phone: str, role: str, expire_at: str | None) -> dict:
        self._require_member_manage(home_id, operator_id)
        existed = self.members.find_by_home_and_phone(home_id, phone)
        if existed and existed.status in {"ACTIVE", "PENDING", "INVITED"}:
            raise AppException(409, "member already exists or pending")
        user = self.users.find_by_phone(phone)
        member = self.members.invite(
            home_id=home_id,
            user_id=user.user_id if user else 0,
            username=user.username if user else "",
            phone=phone,
            role=role,
            expire_at=expire_at,
            invited_by=operator_id,
        )
        self.logs.write(operator_id, home_id, "INVITE_MEMBER", "invite member", "MEMBER", member.member_id)
        return member.__dict__

    def accept_invitation(self, home_id: int, member_id: int, user_id: int) -> dict:
        user = self.users.find_by_id(user_id)
        if not user:
            raise AppException(404, "user not found")
        member = self.members.find_by_id(member_id)
        if not member or member.home_id != home_id:
            raise AppException(404, "invitation not found")
        accepted = self.members.accept_invitation(member_id, user.user_id, user.username, user.phone)
        if not accepted:
            raise AppException(403, "invitation does not belong to current user")
        self.logs.write(user_id, home_id, "ACCEPT_INVITATION", "accept home invitation", "MEMBER", member_id)
        return accepted.__dict__

    def apply(self, home_id: int, user_id: int, reason: str | None) -> dict:
        user = self.users.find_by_id(user_id)
        if not user:
            raise AppException(404, "user not found")
        existed = self.members.find_by_home_and_user(home_id, user_id) or self.members.find_by_home_and_phone(home_id, user.phone)
        if existed and existed.status in {"ACTIVE", "PENDING", "INVITED"}:
            raise AppException(409, "member already exists or pending")
        member = self.members.apply(home_id, user.user_id, user.username, user.phone, reason)
        self.logs.write(user_id, home_id, "APPLY_MEMBER", "apply to join home", "MEMBER", member.member_id)
        return member.__dict__

    def approve(self, home_id: int, operator_id: int, member_id: int, approved: bool, role: str) -> dict:
        self._require_member_manage(home_id, operator_id)
        member = self.members.find_by_id(member_id)
        if not member or member.home_id != home_id:
            raise AppException(404, "member not found")
        updated = self.members.approve(member_id, approved, role)
        if not updated:
            raise AppException(400, "member status cannot be approved")
        self.logs.write(operator_id, home_id, "APPROVE_MEMBER", "approve member", "MEMBER", member_id)
        return updated.__dict__

    def list_members(self, home_id: int, user_id: int) -> list[dict]:
        self.permissions.require_home_permission(home_id, user_id, Permission.HOME_VIEW)
        return [member.__dict__ for member in self.members.list_by_home(home_id)]

    def update_permission(self, home_id: int, operator_id: int, member_id: int, role: str, expire_at: str | None) -> dict:
        self._require_member_manage(home_id, operator_id)
        member = self.members.find_by_id(member_id)
        if not member or member.home_id != home_id:
            raise AppException(404, "member not found")
        updated = self.members.update_permission(member_id, role, expire_at)
        if not updated:
            raise AppException(400, "only active member permission can be updated")
        self.logs.write(operator_id, home_id, "UPDATE_MEMBER_PERMISSION", "update member permission", "MEMBER", member_id)
        return updated.__dict__

    def remove(self, home_id: int, operator_id: int, member_id: int) -> dict:
        self._require_member_manage(home_id, operator_id)
        member = self.members.find_by_id(member_id)
        if not member or member.home_id != home_id:
            raise AppException(404, "member not found")
        if member.user_id == operator_id:
            raise AppException(400, "cannot remove yourself")
        if not self.members.remove(member_id):
            raise AppException(404, "member not found")
        self.logs.write(operator_id, home_id, "REMOVE_MEMBER", "remove member", "MEMBER", member_id)
        return {"status": "removed"}
