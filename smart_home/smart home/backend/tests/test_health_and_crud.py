from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def login(phone: str = "13800000000", password: str = "123456") -> str:
    response = client.post("/api/auth/login", json={"phone": phone, "password": password})
    assert response.status_code == 200
    return response.json()["data"]["token"]


def auth_headers(phone: str = "13800000000") -> dict[str, str]:
    return {"Authorization": f"Bearer {login(phone)}"}


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["data"]["status"] == "ok"


def test_room_and_device_list():
    headers = auth_headers()
    rooms = client.get("/api/homes/1/rooms", headers=headers)
    assert rooms.status_code == 200
    assert len(rooms.json()["data"]) >= 3

    devices = client.get("/api/homes/1/devices", headers=headers)
    assert devices.status_code == 200
    assert len(devices.json()["data"]) >= 6


def test_cannot_delete_room_with_devices():
    response = client.delete("/api/rooms/1", headers=auth_headers())
    assert response.status_code == 400
    assert response.json()["message"] == "该房间下存在设备，不能删除"


def test_control_light_on_and_off():
    turn_on = client.post(
        "/api/devices/1/control",
        headers=auth_headers("13900000000"),
        json={"action": "switch", "target_state": "on", "param_value": None},
    )
    assert turn_on.status_code == 200
    assert turn_on.json()["data"]["device_status"] == "on"

    turn_off = client.post(
        "/api/devices/1/control",
        headers=auth_headers("13900000000"),
        json={"action": "switch", "target_state": "off", "param_value": None},
    )
    assert turn_off.status_code == 200
    assert turn_off.json()["data"]["device_status"] == "off"


def test_sensor_device_cannot_be_controlled():
    response = client.post(
        "/api/devices/3/control",
        headers=auth_headers("13900000000"),
        json={"action": "switch", "target_state": "off", "param_value": None},
    )
    assert response.status_code == 400
    assert response.json()["message"] == "传感器类设备不允许控制"


def test_control_missing_device_returns_404():
    response = client.post(
        "/api/devices/999/control",
        headers=auth_headers(),
        json={"action": "switch", "target_state": "on", "param_value": None},
    )
    assert response.status_code == 404
    assert response.json()["message"] == "设备不存在"


def test_list_operation_logs():
    response = client.get("/api/homes/1/logs", headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["code"] == 200
    assert isinstance(response.json()["data"], list)


def test_control_device_writes_operation_log():
    headers = auth_headers()
    before = client.get("/api/homes/1/logs", headers=headers).json()["data"]

    response = client.post(
        "/api/devices/1/control",
        headers=headers,
        json={"action": "switch", "target_state": "on", "param_value": None},
    )
    assert response.status_code == 200

    after = client.get("/api/homes/1/logs", headers=headers).json()["data"]
    assert len(after) == len(before) + 1
    latest = after[-1]
    assert latest["operation_type"] == "device_control"
    assert latest["operation_object"] == "device:1"
    assert latest["operation_result"] == "success"


def test_scene_execute_updates_devices():
    response = client.post("/api/scenes/1/execute", headers=auth_headers("13900000000"))
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["data"]["scene_id"] == 1
    assert all(item["success"] for item in body["data"]["results"])


def test_create_schedule_and_disable_it():
    created = client.post(
        "/api/homes/1/schedules",
        headers=auth_headers(),
        json={
            "device_id": 1,
            "task_name": "晚上关灯",
            "execute_time": "2026-07-02 22:00:00",
            "action": "switch:off",
            "status": "enabled",
        },
    )
    assert created.status_code == 200
    task = created.json()["data"]
    assert task["task_name"] == "晚上关灯"

    disabled = client.put(
        f"/api/schedules/{task['task_id']}/status",
        headers=auth_headers(),
        json={"status": "disabled"},
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"]["status"] == "disabled"


def test_create_and_list_linkage_rule():
    created = client.post(
        "/api/homes/1/linkages",
        headers=auth_headers(),
        json={
            "rule_name": "烟雾报警联动",
            "trigger_condition": {"device_id": 4, "metric": "smoke", "op": ">", "value": 70},
            "action_config": {"device_id": 1, "action": "switch", "target_state": "on"},
            "enabled": True,
        },
    )
    assert created.status_code == 200
    assert created.json()["data"]["rule_name"] == "烟雾报警联动"

    rules = client.get("/api/homes/1/linkages", headers=auth_headers())
    assert rules.status_code == 200
    assert any(rule["rule_name"] == "烟雾报警联动" for rule in rules.json()["data"])


def test_alarm_detail_and_confirm():
    detail = client.get("/api/alarms/1", headers=auth_headers())
    assert detail.status_code == 200
    assert "process_logs" in detail.json()["data"]

    confirmed = client.post(
        "/api/alarms/1/confirm",
        headers=auth_headers(),
        json={"process_desc": "已收到厨房烟雾报警", "process_result": "success"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["data"]["alarm_status"] == "confirmed"
    assert confirmed.json()["data"]["process_logs"][-1]["action_type"] == "confirm"


def test_device_self_check():
    response = client.post("/api/devices/1/self-check", headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["data"]["check_result"] in {"normal", "offline", "fault"}

    records = client.get("/api/devices/1/self-checks", headers=auth_headers())
    assert records.status_code == 200
    assert len(records.json()["data"]) >= 1


def test_device_simulation_can_trigger_alarm():
    simulated = client.post(
        "/api/devices/4/simulate",
        headers=auth_headers(),
        json={
            "metric_name": "smoke",
            "metric_value": 90,
            "device_status": "online",
            "trigger_alarm": True,
            "alarm_type": "smoke",
            "alarm_level": "danger",
        },
    )
    assert simulated.status_code == 200
    record = simulated.json()["data"]
    assert record["metric_name"] == "smoke"
    assert record["alarm_id"] is not None
    assert record["alarm"]["alarm_level"] == "danger"

    records = client.get("/api/devices/4/simulations", headers=auth_headers())
    assert records.status_code == 200
    assert any(item["simulation_id"] == record["simulation_id"] for item in records.json()["data"])


def test_protected_device_api_requires_token():
    response = client.get("/api/homes/1/devices")
    assert response.status_code == 401
    assert response.json() == {"code": 401, "message": "unauthorized", "data": None}


def test_guest_can_view_but_cannot_control_or_manage_device():
    guest_headers = auth_headers("13700000000")

    viewed = client.get("/api/homes/1/devices", headers=guest_headers)
    assert viewed.status_code == 200

    controlled = client.post(
        "/api/devices/1/control",
        headers=guest_headers,
        json={"action": "switch", "target_state": "on", "param_value": None},
    )
    assert controlled.status_code == 403
    assert controlled.json()["message"] == "permission denied"

    created = client.post(
        "/api/homes/1/devices",
        headers=guest_headers,
        json={
            "room_id": 1,
            "device_name": "访客不应新增的设备",
            "device_type": "light",
            "device_status": "off",
            "is_key_device": False,
        },
    )
    assert created.status_code == 403
    assert created.json()["message"] == "permission denied"
