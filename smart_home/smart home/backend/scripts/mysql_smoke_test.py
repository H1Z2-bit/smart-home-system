from fastapi.testclient import TestClient
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def main() -> None:
    client = TestClient(app)

    health = client.get("/api/health")
    assert health.status_code == 200, health.text

    login = client.post(
        "/api/auth/login",
        json={"phone": "13800000000", "password": "123456"},
    )
    assert login.status_code == 200, login.text
    body = login.json()
    assert body["code"] == 200, body
    token = body["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile = client.get("/api/users/profile", headers=headers)
    assert profile.status_code == 200, profile.text

    homes = client.get("/api/homes", headers=headers)
    assert homes.status_code == 200, homes.text
    home_id = homes.json()["data"][0]["home_id"]

    rooms = client.get(f"/api/homes/{home_id}/rooms", headers=headers)
    assert rooms.status_code == 200, rooms.text

    devices = client.get(f"/api/homes/{home_id}/devices", headers=headers)
    assert devices.status_code == 200, devices.text

    alarms = client.get(f"/api/homes/{home_id}/alarms", headers=headers)
    assert alarms.status_code == 200, alarms.text

    print("MySQL smoke test passed.")


if __name__ == "__main__":
    main()
