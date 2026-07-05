from fastapi.testclient import TestClient

from app.api.v1.debug import reset_all_mock_data
from app.main import app


client = TestClient(app)


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def login(phone: str = "13800000000", password: str = "123456") -> dict:
    response = client.post("/api/auth/login", json={"phone": phone, "password": password})
    assert response.status_code == 200
    return response.json()["data"]


def send_code(phone: str, scene: str = "login", headers: dict | None = None) -> str:
    response = client.post("/api/auth/sms/send", json={"phone": phone, "scene": scene}, headers=headers or {})
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    return body["data"]["mock_code"]


def test_sms_login_existing_verified_phone_returns_same_account():
    reset_all_mock_data()

    code = send_code("13800000000")
    response = client.post("/api/auth/sms/login", json={"phone": "13800000000", "code": code})
    body = response.json()

    assert response.status_code == 200
    assert body["code"] == 200
    assert body["data"]["user"]["user_id"] == 1
    assert body["data"]["user"]["phone_verified"] is True

    profile = client.get("/api/users/profile", headers=auth_headers(body["data"]["token"])).json()
    assert profile["data"]["user_id"] == 1


def test_sms_login_new_phone_auto_registers_verified_account():
    reset_all_mock_data()

    phone = "15500001111"
    code = send_code(phone)
    response = client.post("/api/auth/sms/login", json={"phone": phone, "code": code})
    body = response.json()

    assert response.status_code == 200
    assert body["code"] == 200
    assert body["data"]["user"]["phone"] == phone
    assert body["data"]["user"]["phone_verified"] is True
    assert body["data"]["user"]["phone_bound"] is True


def test_password_registered_user_can_bind_phone_then_sms_login_same_account():
    reset_all_mock_data()

    phone = "15600002222"
    register = client.post(
        "/api/auth/register",
        json={"username": "bind_user", "phone": phone, "password": "123456"},
    ).json()
    assert register["code"] == 200

    password_login = login(phone)
    user_id = password_login["user"]["user_id"]
    assert password_login["user"]["phone_verified"] is False
    assert password_login["user"]["phone_bound"] is False

    bind_code_response = client.post(
        "/api/users/phone/code",
        json={"phone": phone, "scene": "bind"},
        headers=auth_headers(password_login["token"]),
    ).json()
    bind_code = bind_code_response["data"]["mock_code"]

    bind = client.post(
        "/api/users/phone/bind",
        json={"phone": phone, "code": bind_code},
        headers=auth_headers(password_login["token"]),
    ).json()
    assert bind["code"] == 200
    assert bind["data"]["phone_verified"] is True

    code = send_code(phone)
    sms_login = client.post("/api/auth/sms/login", json={"phone": phone, "code": code}).json()
    assert sms_login["code"] == 200
    assert sms_login["data"]["user"]["user_id"] == user_id


def test_cannot_bind_phone_used_by_another_verified_account():
    reset_all_mock_data()

    token = login("13900000000")["token"]
    bind_code = client.post(
        "/api/users/phone/code",
        json={"phone": "13800000000", "scene": "bind"},
        headers=auth_headers(token),
    ).json()["data"]["mock_code"]

    response = client.post(
        "/api/users/phone/bind",
        json={"phone": "13800000000", "code": bind_code},
        headers=auth_headers(token),
    )
    body = response.json()

    assert response.status_code == 409
    assert body["code"] == 409


def test_public_sms_send_only_supports_login_scene():
    reset_all_mock_data()

    response = client.post("/api/auth/sms/send", json={"phone": "15600003333", "scene": "bind"})
    body = response.json()

    assert response.status_code == 400
    assert body["code"] == 400
