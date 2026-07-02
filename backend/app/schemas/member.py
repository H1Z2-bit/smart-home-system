from pydantic import BaseModel, Field


class MemberInviteRequest(BaseModel):
    phone: str
    role: str = "MEMBER"
    expire_at: str | None = None


class MemberApplyRequest(BaseModel):
    reason: str | None = None


class MemberApproveRequest(BaseModel):
    approved: bool = True
    role: str = "MEMBER"


class MemberPermissionRequest(BaseModel):
    role: str = Field(pattern="^(OWNER|MEMBER|GUEST|MAINTAINER)$")
    expire_at: str | None = None


class MemberInfo(BaseModel):
    member_id: int
    home_id: int
    user_id: int
    username: str
    phone: str
    role: str
    status: str
    expire_at: str | None = None
    invited_by: int | None = None
    apply_reason: str | None = None
    created_at: str | None = None