from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def login(phone: str = "13800000000", password: str = "123456") -> str:
    response = client.post("/api/auth/login", json={"phone": phone, "password": password})
    body = response.json()
    assert response.status_code == 200
    assert body["code"] == 200
    return body["data"]["token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_login_and_profile():
    token = login()

    response = client.get("/api/users/profile", headers=auth_headers(token))
    body = response.json()

    assert response.status_code == 200
    assert body["code"] == 200
    assert body["data"]["username"] == "han"
    assert body["data"]["role"] == "OWNER"


def test_profile_requires_token():
    response = client.get("/api/users/profile")
    body = response.json()

    assert response.status_code == 401
    assert body["code"] == 401


def test_home_member_system_config_and_system_logs_flow():
    token = login()
    headers = auth_headers(token)

    homes = client.get("/api/homes", headers=headers).json()
    assert homes["code"] == 200
    assert homes["data"][0]["home_id"] == 1

    home = client.get("/api/homes/1", headers=headers).json()
    assert home["code"] == 200
    assert home["data"]["name"] == "演示家庭"

    members = client.get("/api/homes/1/members", headers=headers).json()
    assert members["code"] == 200
    assert any(member["role"] == "OWNER" for member in members["data"])

    config = client.get("/api/homes/1/system/config", headers=headers).json()
    assert config["code"] == 200
    assert config["data"]["simulation_enabled"] is True

    updated = client.put(
        "/api/homes/1/system/config",
        headers=headers,
        json={"temperature_high_threshold": 36.5, "simulation_enabled": False},
    ).json()
    assert updated["code"] == 200
    assert updated["data"]["temperature_high_threshold"] == 36.5

    logs = client.get("/api/homes/1/system/logs", headers=headers).json()
    assert logs["code"] == 200
    assert any(log["action"] == "UPDATE_SYSTEM_CONFIG" for log in logs["data"])


def test_member_cannot_update_system_config():
    token = login("13900000000")

    response = client.put(
        "/api/homes/1/system/config",
        headers=auth_headers(token),
        json={"simulation_enabled": True},
    )
    body = response.json()

    assert response.status_code == 403
    assert body["code"] == 403


def test_device_operation_logs_require_auth_and_owner_can_view():
    response = client.get("/api/homes/1/logs")
    assert response.status_code == 401
    assert response.json()["code"] == 401

    owner_response = client.get("/api/homes/1/logs", headers=auth_headers(login()))
    assert owner_response.status_code == 200
    assert owner_response.json()["code"] == 200
    assert isinstance(owner_response.json()["data"], list)
