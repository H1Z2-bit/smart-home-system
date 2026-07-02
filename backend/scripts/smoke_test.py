import json
import sys
import urllib.error
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"


def request(method: str, path: str, body: dict | None = None, token: str | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read().decode("utf-8"))


def assert_ok(name: str, resp: dict) -> None:
    if resp.get("code") != 200:
        raise SystemExit(f"{name} failed: {resp}")
    print(f"[OK] {name}")


def main() -> None:
    assert_ok("health", request("GET", "/api/health"))
    login = request("POST", "/api/auth/login", {"phone": "13800000000", "password": "123456"})
    assert_ok("login", login)
    token = login["data"]["token"]
    assert_ok("profile", request("GET", "/api/users/profile", token=token))
    assert_ok("homes", request("GET", "/api/homes", token=token))
    assert_ok("members", request("GET", "/api/homes/1/members", token=token))
    assert_ok("system config", request("GET", "/api/homes/1/system/config", token=token))


if __name__ == "__main__":
    main()