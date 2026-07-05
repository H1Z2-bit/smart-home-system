import os
import shutil
import subprocess
from pathlib import Path

import pytest

os.environ["USE_MOCK_REPOSITORY"] = "false"

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MYSQL_TESTS") != "1",
    reason="set RUN_MYSQL_TESTS=1 to run MySQL integration tests",
)


def _import_schema() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    sql_file = backend_dir.parents[1] / "smart_home.sql"
    mysql_exe = _resolve_mysql_exe()
    from app.core.config import settings

    password = os.getenv("DATABASE_PASSWORD", settings.database_password)
    user = os.getenv("DATABASE_USER", settings.database_user)
    if not password:
        pytest.fail("DATABASE_PASSWORD is required for MySQL integration tests")

    env = os.environ.copy()
    env["MYSQL_PWD"] = password
    with sql_file.open("rb") as stdin:
        subprocess.run(
            [
                mysql_exe,
                f"-u{user}",
                "--default-character-set=utf8mb4",
                "--binary-mode=1",
            ],
            stdin=stdin,
            env=env,
            check=True,
        )


def _resolve_mysql_exe() -> str:
    candidates = [
        os.getenv("MYSQL_EXE"),
        r"D:\coding\MySQL\bin\mysql.exe",
        r"D:\MySQL\MySQL Server 8.0\bin\mysql.exe",
        shutil.which("mysql"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    pytest.fail("mysql.exe not found. Set MYSQL_EXE to your local mysql.exe path.")


@pytest.fixture(scope="session", autouse=True)
def mysql_schema():
    _import_schema()


@pytest.fixture()
def client(mysql_schema):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/api/auth/login",
        json={"phone": "13800000000", "password": "123456"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def member_auth_headers(client):
    response = client.post(
        "/api/auth/login",
        json={"phone": "13900000000", "password": "123456"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def test_mysql_auth_home_and_profile(client, auth_headers):
    profile = client.get("/api/users/profile", headers=auth_headers)
    assert profile.status_code == 200, profile.text
    assert profile.json()["data"]["phone"] == "13800000000"

    homes = client.get("/api/homes", headers=auth_headers)
    assert homes.status_code == 200, homes.text
    assert homes.json()["data"][0]["name"] == "演示家庭"

    config = client.get("/api/homes/1/system/config", headers=auth_headers)
    assert config.status_code == 200, config.text
    assert config.json()["data"]["simulation_enabled"] is True


def test_mysql_room_and_device_crud(client, auth_headers):
    room_payload = {
        "room_name": "测试书房",
        "room_type": "study",
        "remark": "MySQL pytest room",
    }
    created_room = client.post("/api/homes/1/rooms", headers=auth_headers, json=room_payload)
    assert created_room.status_code == 200, created_room.text
    room_id = created_room.json()["data"]["room_id"]

    updated_room = client.put(
        f"/api/rooms/{room_id}",
        headers=auth_headers,
        json={"room_name": "测试书房A", "room_type": "study", "remark": "updated"},
    )
    assert updated_room.status_code == 200, updated_room.text
    assert updated_room.json()["data"]["room_name"] == "测试书房A"

    device_payload = {
        "room_id": room_id,
        "device_name": "测试台灯",
        "device_type": "light",
        "device_status": "off",
        "is_key_device": False,
    }
    created_device = client.post("/api/homes/1/devices", headers=auth_headers, json=device_payload)
    assert created_device.status_code == 200, created_device.text
    device_id = created_device.json()["data"]["device_id"]

    from app.repositories.factory import get_device_event_repository, get_operation_log_repository

    device_event_repository = get_device_event_repository()
    operation_log_repository = get_operation_log_repository()
    events_before_control = device_event_repository.list_by_device(device_id)

    controlled = client.post(
        f"/api/devices/{device_id}/control",
        headers=auth_headers,
        json={"action": "switch", "target_state": "on"},
    )
    assert controlled.status_code == 200, controlled.text
    assert controlled.json()["data"]["device_status"] == "on"

    events_after_control = device_event_repository.list_by_device(device_id)
    assert len(events_after_control) == len(events_before_control) + 1
    latest_event = events_after_control[0]
    assert latest_event["event_type"] == "control"
    assert latest_event["old_status"] == "off"
    assert latest_event["new_status"] == "on"
    assert latest_event["operator_id"] == 1

    latest_control_log = next(
        log
        for log in operation_log_repository.list_by_home(1)
        if log["operation_type"] == "device_control" and log["operation_object"] == f"device:{device_id}"
    )
    assert latest_control_log["operator_id"] == 1

    device_detail = client.get("/api/devices/1", headers=auth_headers)
    assert device_detail.status_code == 200, device_detail.text
    device = device_detail.json()["data"]
    assert device["manufacturer"] == "DemoSmart"
    assert device["model"] == "LIGHT-A1"
    assert device["serial_no"] == "SH-DEV-0001"
    assert device["layout"]["position_x"] == 1.2

    delete_device = client.delete(f"/api/devices/{device_id}", headers=auth_headers)
    assert delete_device.status_code == 200, delete_device.text

    delete_room = client.delete(f"/api/rooms/{room_id}", headers=auth_headers)
    assert delete_room.status_code == 200, delete_room.text


def test_mysql_member_operator_id_for_device_control(client, member_auth_headers):
    from app.repositories.factory import get_device_event_repository, get_operation_log_repository

    controlled = client.post(
        "/api/devices/1/control",
        headers=member_auth_headers,
        json={"action": "switch", "target_state": "off"},
    )
    assert controlled.status_code == 200, controlled.text

    latest_event = get_device_event_repository().list_by_device(1)[0]
    assert latest_event["event_type"] == "control"
    assert latest_event["operator_id"] == 2

    latest_log = next(
        log
        for log in get_operation_log_repository().list_by_home(1)
        if log["operation_type"] == "device_control" and log["operation_object"] == "device:1"
    )
    assert latest_log["operator_id"] == 2


def test_mysql_scene_schedule_and_linkage(client, auth_headers):
    scene = client.post(
        "/api/homes/1/scenes",
        headers=auth_headers,
        json={
            "scene_name": "测试开灯模式",
            "enabled": True,
            "actions": [{"device_id": 1, "target_state": "on", "sort_no": 1}],
        },
    )
    assert scene.status_code == 200, scene.text
    scene_id = scene.json()["data"]["scene_id"]

    executed = client.post(f"/api/scenes/{scene_id}/execute", headers=auth_headers)
    assert executed.status_code == 200, executed.text
    assert executed.json()["data"]["results"][0]["success"] is True

    schedule = client.post(
        "/api/homes/1/schedules",
        headers=auth_headers,
        json={
            "device_id": 1,
            "task_name": "测试定时关灯",
            "execute_time": "2026-07-05 22:30:00",
            "action": "off",
            "status": "enabled",
        },
    )
    assert schedule.status_code == 200, schedule.text
    task_id = schedule.json()["data"]["task_id"]

    status = client.put(f"/api/schedules/{task_id}/status", headers=auth_headers, json={"status": "disabled"})
    assert status.status_code == 200, status.text
    assert status.json()["data"]["status"] == "disabled"

    linkage = client.post(
        "/api/homes/1/linkages",
        headers=auth_headers,
        json={
            "rule_name": "测试烟雾联动",
            "trigger_condition": {"device_id": 4, "data_type": "smoke", "operator": ">", "threshold": 60},
            "action_config": {"device_id": 1, "target_state": "on"},
            "enabled": True,
            "created_by": 1,
        },
    )
    assert linkage.status_code == 200, linkage.text
    rule_id = linkage.json()["data"]["rule_id"]

    assert client.delete(f"/api/linkages/{rule_id}", headers=auth_headers).status_code == 200
    assert client.delete(f"/api/schedules/{task_id}", headers=auth_headers).status_code == 200
    assert client.delete(f"/api/scenes/{scene_id}", headers=auth_headers).status_code == 200


def test_mysql_simulation_alarm_self_check_and_logs(client, auth_headers):
    simulation = client.post(
        "/api/devices/4/simulate",
        headers=auth_headers,
        json={
            "metric_name": "smoke",
            "metric_value": 92,
            "device_status": "online",
            "trigger_alarm": True,
            "alarm_type": "smoke",
            "alarm_level": "serious",
            "simulation_type": "scenario",
            "scenario_name": "厨房烟雾升高演示",
        },
    )
    assert simulation.status_code == 200, simulation.text
    data = simulation.json()["data"]
    assert data["trigger_alarm"] is True
    assert data["alarm_type"] == "smoke"
    assert data["alarm_level"] == "serious"
    assert data["simulation_type"] == "scenario"
    assert data["scenario_name"] == "厨房烟雾升高演示"
    assert data["alarm_id"] is not None

    alarm_id = data["alarm_id"]
    detail = client.get(f"/api/alarms/{alarm_id}", headers=auth_headers)
    assert detail.status_code == 200, detail.text
    assert detail.json()["data"]["process_logs"]

    processed = client.post(
        f"/api/alarms/{alarm_id}/process",
        headers=auth_headers,
        json={"process_desc": "pytest process", "process_result": "success"},
    )
    assert processed.status_code == 200, processed.text
    processed_data = processed.json()["data"]
    assert processed_data["alarm_status"] == "processing"
    assert processed_data["processed_by"] == 1
    assert processed_data["process_logs"][-1]["handler_id"] == 1

    normal_simulation = client.post(
        "/api/devices/3/simulate",
        headers=auth_headers,
        json={
            "metric_name": "temperature",
            "metric_value": 26.5,
            "device_status": "online",
            "trigger_alarm": False,
            "alarm_type": None,
            "alarm_level": "notice",
            "simulation_type": "manual",
            "scenario_name": None,
        },
    )
    assert normal_simulation.status_code == 200, normal_simulation.text
    normal_data = normal_simulation.json()["data"]
    assert normal_data["trigger_alarm"] is False
    assert normal_data["alarm_id"] is None
    assert normal_data["alarm_type"] is None
    assert normal_data["alarm_level"] == "notice"
    assert normal_data["simulation_type"] == "manual"
    assert normal_data["scenario_name"] is None

    self_check = client.post("/api/devices/4/self-check", headers=auth_headers)
    assert self_check.status_code == 200, self_check.text
    self_check_data = self_check.json()["data"]
    assert self_check_data["check_result"] == "normal"
    assert self_check_data["operator_id"] == 1

    logs = client.get("/api/homes/1/logs", headers=auth_headers)
    assert logs.status_code == 200, logs.text
    assert any(log["operation_type"] for log in logs.json()["data"])
