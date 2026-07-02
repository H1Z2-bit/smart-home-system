from jose import jwt
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def login(phone: str = "13800000000", password: str = "123456") -> str:
    response = client.post("/api/auth/login", json={"phone": phone, "password": password})
    body = response.json()
    assert response.status_code == 200
    assert body["code"] == 200
    return body["data"]["token"]


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    response = client.get("/api/health")
    body = response.json()
    assert response.status_code == 200
    assert body["code"] == 200
    assert body["data"]["status"] == "ok"


def test_login_uses_rs256_when_keys_exist_and_profile_works():
    token = login()
    assert jwt.get_unverified_header(token)["alg"] == "RS256"

    response = client.get("/api/users/profile", headers=headers(token))
    body = response.json()
    assert body["code"] == 200
    assert body["data"]["username"] == "han"
    assert body["data"]["role"] == "OWNER"


def test_profile_requires_token():
    response = client.get("/api/users/profile")
    body = response.json()
    assert body["code"] == 401


def test_home_member_config_and_logs_flow():
    token = login()
    auth = headers(token)

    homes = client.get("/api/homes", headers=auth).json()
    assert homes["code"] == 200
    assert homes["data"][0]["home_id"] == 1

    home = client.get("/api/homes/1", headers=auth).json()
    assert home["code"] == 200
    assert home["data"]["name"] == "演示家庭"

    members = client.get("/api/homes/1/members", headers=auth).json()
    assert members["code"] == 200
    assert any(member["role"] == "OWNER" for member in members["data"])

    config = client.get("/api/homes/1/system/config", headers=auth).json()
    assert config["code"] == 200
    assert config["data"]["simulation_enabled"] is True

    updated = client.put(
        "/api/homes/1/system/config",
        headers=auth,
        json={"temperature_high_threshold": 36.5, "simulation_enabled": False},
    ).json()
    assert updated["code"] == 200
    assert updated["data"]["temperature_high_threshold"] == 36.5
    assert updated["data"]["simulation_enabled"] is False

    logs = client.get("/api/homes/1/logs", headers=auth).json()
    assert logs["code"] == 200
    assert any(log["action"] == "UPDATE_SYSTEM_CONFIG" for log in logs["data"])


def test_member_cannot_update_system_config():
    token = login("13900000000")
    response = client.put(
        "/api/homes/1/system/config",
        headers=headers(token),
        json={"simulation_enabled": True},
    )
    body = response.json()
    assert body["code"] == 403


def test_invite_accept_invitation_flow():
    owner_token = login()
    invite = client.post(
        "/api/homes/1/members/invite",
        headers=headers(owner_token),
        json={"phone": "13600000000", "role": "MAINTAINER"},
    ).json()
    assert invite["code"] == 200
    assert invite["data"]["status"] == "INVITED"
    member_id = invite["data"]["member_id"]

    maintainer_token = login("13600000000")
    accepted = client.post(f"/api/homes/1/members/{member_id}/accept", headers=headers(maintainer_token)).json()
    assert accepted["code"] == 200
    assert accepted["data"]["status"] == "ACTIVE"
    assert accepted["data"]["role"] == "MAINTAINER"


def test_apply_duplicate_member_is_rejected():
    member_token = login("13900000000")
    response = client.post(
        "/api/homes/1/members/apply",
        headers=headers(member_token),
        json={"reason": "I live here"},
    )
    body = response.json()
    assert body["code"] == 409