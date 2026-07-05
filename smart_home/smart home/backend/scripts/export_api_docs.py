import json
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.main import app

DOCS_DIR = BASE_DIR / "docs"
OPENAPI_PATH = DOCS_DIR / "openapi.json"
POSTMAN_PATH = DOCS_DIR / "smart_home_api.postman_collection.json"


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    openapi = app.openapi()
    write_json(OPENAPI_PATH, openapi)
    write_json(POSTMAN_PATH, build_postman_collection(openapi))
    print(f"Exported {OPENAPI_PATH}")
    print(f"Exported {POSTMAN_PATH}")


def build_postman_collection(openapi: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for path, path_item in openapi.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.upper() not in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
                continue
            tag = (operation.get("tags") or ["默认接口"])[0]
            grouped.setdefault(tag, []).append(build_postman_item(path, method.upper(), operation))

    return {
        "info": {
            "name": "智能家居综合管理系统 API",
            "description": "由 FastAPI OpenAPI 自动导出的 Postman Collection。",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{token}}", "type": "string"}],
        },
        "variable": [
            {"key": "base_url", "value": "http://127.0.0.1:8000"},
            {"key": "token", "value": ""},
        ],
        "item": [{"name": tag, "item": items} for tag, items in grouped.items()],
    }


def build_postman_item(path: str, method: str, operation: dict[str, Any]) -> dict[str, Any]:
    request: dict[str, Any] = {
        "method": method,
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "url": {
            "raw": "{{base_url}}" + path,
            "host": ["{{base_url}}"],
            "path": [part for part in path.strip("/").split("/") if part],
        },
        "description": operation.get("summary") or operation.get("description") or "",
    }
    if method in {"POST", "PUT", "PATCH"}:
        request["body"] = {
            "mode": "raw",
            "raw": json.dumps(example_body(operation), ensure_ascii=False, indent=2),
            "options": {"raw": {"language": "json"}},
        }
    return {
        "name": operation.get("summary") or operation.get("operationId") or f"{method} {path}",
        "request": request,
        "response": [],
    }


def example_body(operation: dict[str, Any]) -> dict[str, Any]:
    schema = (
        operation.get("requestBody", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    if "properties" in schema:
        return {key: example_value(value) for key, value in schema["properties"].items()}
    return {}


def example_value(schema: dict[str, Any]) -> Any:
    if "default" in schema:
        return schema["default"]
    schema_type = schema.get("type")
    if schema_type == "integer":
        return 1
    if schema_type == "number":
        return 1.0
    if schema_type == "boolean":
        return True
    if schema_type == "array":
        return []
    if schema_type == "object":
        return {}
    return ""


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
