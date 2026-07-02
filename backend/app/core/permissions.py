from enum import StrEnum


class Role(StrEnum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"
    GUEST = "GUEST"
    MAINTAINER = "MAINTAINER"
    SYSTEM = "SYSTEM"


class Permission(StrEnum):
    HOME_VIEW = "HOME_VIEW"
    HOME_MANAGE = "HOME_MANAGE"
    MEMBER_MANAGE = "MEMBER_MANAGE"
    SYSTEM_CONFIG = "SYSTEM_CONFIG"
    LOG_VIEW = "LOG_VIEW"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.OWNER: {Permission.HOME_VIEW, Permission.HOME_MANAGE, Permission.MEMBER_MANAGE, Permission.SYSTEM_CONFIG, Permission.LOG_VIEW},
    Role.MEMBER: {Permission.HOME_VIEW, Permission.LOG_VIEW},
    Role.GUEST: {Permission.HOME_VIEW},
    Role.MAINTAINER: {Permission.HOME_VIEW, Permission.LOG_VIEW},
    Role.SYSTEM: {Permission.HOME_VIEW, Permission.HOME_MANAGE, Permission.MEMBER_MANAGE, Permission.SYSTEM_CONFIG, Permission.LOG_VIEW},
}


def has_permission(role: str, permission: Permission) -> bool:
    try:
        role_enum = Role(role)
    except ValueError:
        return False
    return permission in ROLE_PERMISSIONS.get(role_enum, set())