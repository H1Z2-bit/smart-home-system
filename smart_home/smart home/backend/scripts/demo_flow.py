import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def request(method: str, url: str, token: str | None = None, body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        content = exc.read().decode("utf-8")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"code": exc.code, "message": content, "data": None}


def step(title: str, result: dict[str, Any]) -> dict[str, Any]:
    print(f"\n== {title} ==")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="智能家居后端演示流程脚本")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="后端服务地址")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    step("健康检查", request("GET", f"{base}/api/health"))
    step("重置 Mock 演示数据", request("POST", f"{base}/api/debug/reset"))

    login = step("户主登录", request("POST", f"{base}/api/auth/login", body={"phone": "13800000000", "password": "123456"}))
    if login.get("code") != 200:
        print("登录失败，请确认后端已启动。", file=sys.stderr)
        return 1
    owner_token = login["data"]["token"]

    step("查询家庭空间", request("GET", f"{base}/api/homes", token=owner_token))
    step("查询家庭成员", request("GET", f"{base}/api/homes/1/members", token=owner_token))

    new_phone = "13500008001"
    step("注册待邀请成员", request("POST", f"{base}/api/auth/register", body={"username": "demo_member", "phone": new_phone, "password": "123456"}))
    member_login = step("待邀请成员登录", request("POST", f"{base}/api/auth/login", body={"phone": new_phone, "password": "123456"}))
    member_token = member_login["data"]["token"]

    invite = step(
        "户主邀请成员",
        request("POST", f"{base}/api/homes/1/members/invite", token=owner_token, body={"phone": new_phone, "role": "GUEST"}),
    )
    member_id = invite["data"]["member_id"]
    step("成员接受邀请", request("POST", f"{base}/api/homes/1/members/{member_id}/accept", token=member_token))
    step("户主调整成员权限", request("PUT", f"{base}/api/homes/1/members/{member_id}/permission", token=owner_token, body={"role": "MEMBER"}))

    step("修改系统配置", request("PUT", f"{base}/api/homes/1/system/config", token=owner_token, body={"simulation_enabled": True, "temperature_high_threshold": 36.5}))
    step("控制客厅灯", request("POST", f"{base}/api/devices/1/control", body={"action": "switch", "target_state": "on", "param_value": None}))
    step("模拟烟雾报警", request("POST", f"{base}/api/devices/4/simulate", body={"metric_name": "smoke", "metric_value": 90, "device_status": "online", "trigger_alarm": True, "alarm_type": "smoke", "alarm_level": "danger"}))
    step("查询系统日志", request("GET", f"{base}/api/homes/1/system/logs", token=owner_token))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
