from app.core.config import settings


def success(data=None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data}


def fail(code: int, message: str, data=None) -> dict:
    return {"code": code, "message": message, "data": data}


class AppException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)