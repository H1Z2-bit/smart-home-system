from typing import Any


def success_response(data: Any = None, message: str = "success") -> dict[str, Any]:
    if data is None:
        data = {}
    return {
        "code": 200,
        "message": message,
        "data": data,
    }


def error_response(message: str, code: int = 400) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "data": None,
    }


def success(data: Any = None, message: str = "success") -> dict[str, Any]:
    return success_response(data, message)


def fail(code: int, message: str, data: Any = None) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "data": data,
    }


class AppException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
