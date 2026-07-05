from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def login(phone: str = "13800000000", password: str = "123456") -> str:
    response = client.post("/api/auth/login", json={"phone": phone, "password": password})
    body = response.json()
    assert response.status_code == 200
    assert body["code"] == 200
    return body["data"]["token"]


def register_and_login(username: str, phone: str, password: str = "123456") -> str:
    response = client.post(
        "/api/auth/register",
        json={"username": username, "phone": phone, "password": password},
    )
    assert response.status_code == 200
    return login(phone, password)


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_rbac_owner_member_guest_and_non_member_permissions():
    owner_headers = auth_headers(login())
    member_headers = auth_headers(login("13900000000"))
    guest_headers = auth_headers(login("13700000000"))
    non_member_headers = auth_headers(login("13600000000"))

    owner_update = client.put(
        "/api/homes/1/system/config",
        headers=owner_headers,
        json={"simulation_enabled": True, "temperature_high_threshold": 37.0},
    )
    assert owner_update.status_code == 200
    assert owner_update.json()["code"] == 200

    member_update = client.put(
        "/api/homes/1/system/config",
        headers=member_headers,
        json={"simulation_enabled": False},
    )
    assert member_update.status_code == 403
    assert member_update.json()["message"] == "permission denied"

    guest_view = client.get("/api/homes/1/system/config", headers=guest_headers)
    assert guest_view.status_code == 200

    guest_invite = client.post(
        "/api/homes/1/members/invite",
        headers=guest_headers,
        json={"phone": "13500001001", "role": "MEMBER"},
    )
    assert guest_invite.status_code == 403
    assert guest_invite.json()["message"] == "permission denied"

    non_member_view = client.get("/api/homes/1", headers=non_member_headers)
    assert non_member_view.status_code == 403
    assert non_member_view.json()["message"] == "not home member"


def test_member_invitation_accept_permission_update_and_remove_flow():
    owner_headers = auth_headers(login())
    invitee_phone = "13500002001"
    invitee_headers = auth_headers(register_and_login("invitee", invitee_phone))

    invited = client.post(
        "/api/homes/1/members/invite",
        headers=owner_headers,
        json={"phone": invitee_phone, "role": "GUEST", "expire_at": "2026-12-31 23:59:59"},
    )
    assert invited.status_code == 200
    invited_member = invited.json()["data"]
    assert invited_member["status"] == "INVITED"
    assert invited_member["role"] == "GUEST"

    accepted = client.post(
        f"/api/homes/1/members/{invited_member['member_id']}/accept",
        headers=invitee_headers,
    )
    assert accepted.status_code == 200
    accepted_member = accepted.json()["data"]
    assert accepted_member["status"] == "ACTIVE"
    assert accepted_member["phone"] == invitee_phone

    denied_config_update = client.put(
        "/api/homes/1/system/config",
        headers=invitee_headers,
        json={"simulation_enabled": False},
    )
    assert denied_config_update.status_code == 403

    updated_permission = client.put(
        f"/api/homes/1/members/{accepted_member['member_id']}/permission",
        headers=owner_headers,
        json={"role": "MEMBER", "expire_at": None},
    )
    assert updated_permission.status_code == 200
    assert updated_permission.json()["data"]["role"] == "MEMBER"

    removed = client.delete(
        f"/api/homes/1/members/{accepted_member['member_id']}",
        headers=owner_headers,
    )
    assert removed.status_code == 200
    assert removed.json()["data"]["status"] == "removed"

    after_remove = client.get("/api/homes/1/members", headers=owner_headers)
    assert all(member["member_id"] != accepted_member["member_id"] for member in after_remove.json()["data"])


def test_member_apply_owner_approve_and_reject_flow():
    owner_headers = auth_headers(login())
    applicant_headers = auth_headers(register_and_login("applicant", "13500003001"))

    applied = client.post(
        "/api/homes/1/members/apply",
        headers=applicant_headers,
        json={"reason": "希望加入家庭空间进行日常设备查看"},
    )
    assert applied.status_code == 200
    pending_member = applied.json()["data"]
    assert pending_member["status"] == "PENDING"

    approved = client.post(
        f"/api/homes/1/members/{pending_member['member_id']}/approve",
        headers=owner_headers,
        json={"approved": True, "role": "MAINTAINER"},
    )
    assert approved.status_code == 200
    approved_member = approved.json()["data"]
    assert approved_member["status"] == "ACTIVE"
    assert approved_member["role"] == "MAINTAINER"

    maintainer_view = client.get("/api/homes/1/members", headers=applicant_headers)
    assert maintainer_view.status_code == 200

    maintainer_config_update = client.put(
        "/api/homes/1/system/config",
        headers=applicant_headers,
        json={"simulation_enabled": True},
    )
    assert maintainer_config_update.status_code == 403

    reject_headers = auth_headers(register_and_login("reject_user", "13500003002"))
    reject_apply = client.post(
        "/api/homes/1/members/apply",
        headers=reject_headers,
        json={"reason": "临时查看设备"},
    )
    assert reject_apply.status_code == 200
    reject_member = reject_apply.json()["data"]

    rejected = client.post(
        f"/api/homes/1/members/{reject_member['member_id']}/approve",
        headers=owner_headers,
        json={"approved": False, "role": "GUEST"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["data"]["status"] == "REJECTED"

    rejected_view = client.get("/api/homes/1", headers=reject_headers)
    assert rejected_view.status_code == 403
