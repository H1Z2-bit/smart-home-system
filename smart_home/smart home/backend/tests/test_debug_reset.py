from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_debug_reset_restores_mock_data():
    created = client.post(
        "/api/auth/register",
        json={"username": "reset_user", "phone": "13500009001", "password": "123456"},
    )
    assert created.status_code == 200

    reset = client.post("/api/debug/reset")
    body = reset.json()
    assert reset.status_code == 200
    assert body["data"]["status"] == "reset_ok"
    assert body["data"]["users"] == 4
    assert body["data"]["devices"] == 6

    login = client.post("/api/auth/login", json={"phone": "13500009001", "password": "123456"})
    assert login.status_code == 401

    health = client.get("/api/health")
    assert health.status_code == 200
