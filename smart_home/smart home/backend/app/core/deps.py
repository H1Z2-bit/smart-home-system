from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.permissions import Permission, has_permission
from app.core.security import TokenPayload, parse_access_token
from app.utils.response import AppException

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme)) -> TokenPayload:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppException(401, "unauthorized")
    payload = parse_access_token(credentials.credentials)
    if payload is None:
        raise AppException(401, "unauthorized")
    return payload


def require_permission(permission: Permission):
    def checker(current_user: TokenPayload = Security(get_current_user)) -> TokenPayload:
        if not has_permission(current_user.role, permission):
            raise AppException(403, "permission denied")
        return current_user

    return checker