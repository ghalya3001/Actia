"""
===============================================================================
TESTS DU CONTRÔLE D'ACCÈS BASÉ SUR LES RÔLES (RBAC) & VALIDATION DES COMPTES
===============================================================================
"""

import pytest
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password


def create_test_user(db_session, email, role=UserRole.USER.value, status=UserStatus.PENDING.value, password="TestPassword123!"):
    user = User(
        email=email,
        full_name=f"User {email}",
        hashed_password=hash_password(password),
        role=role,
        status=status,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def login_user(client, email, password="TestPassword123!"):
    resp = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    return data["access_token"], data


def test_registration_defaults_to_user_and_pending(client):
    reg_payload = {
        "email": "newbie@platformactia.com",
        "full_name": "Newbie User",
        "password": "SecurePassword123!"
    }
    resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "USER"
    assert data["status"] == "PENDING"
    assert data["rejection_reason"] is None


def test_pending_user_blocked_from_protected_apis(client, db_session):
    # 1. Register new user (PENDING by default)
    user = create_test_user(db_session, "pending_user@actia.com", status=UserStatus.PENDING.value)
    token, login_data = login_user(client, user.email)
    assert login_data["status"] == "PENDING"
    assert login_data["role"] == "USER"

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Can access /me
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["status"] == "PENDING"

    # 3. Blocked with 403 from /audits/
    audit_resp = client.get("/api/v1/audits/", headers=headers)
    assert audit_resp.status_code == 403
    assert "PENDING" in audit_resp.json()["detail"]

    # 4. Blocked with 403 from /dashboard/widgets
    dash_resp = client.get("/api/v1/dashboard/widgets", headers=headers)
    assert dash_resp.status_code == 403


def test_non_admin_blocked_from_admin_endpoints(client, db_session):
    # Approved USER
    user = create_test_user(db_session, "standard_approved@actia.com", role=UserRole.USER.value, status=UserStatus.APPROVED.value)
    token, _ = login_user(client, user.email)
    headers = {"Authorization": f"Bearer {token}"}

    # Blocked from /api/v1/admin/users
    admin_users_resp = client.get("/api/v1/admin/users", headers=headers)
    assert admin_users_resp.status_code == 403
    assert "administrateur" in admin_users_resp.json()["detail"].lower()

    # Blocked from /api/v1/admin/stats
    admin_stats_resp = client.get("/api/v1/admin/stats", headers=headers)
    assert admin_stats_resp.status_code == 403


def test_admin_approval_workflow(client, db_session):
    # 1. Create Admin and Pending User
    admin = create_test_user(db_session, "admin_boss@actia.com", role=UserRole.ADMIN.value, status=UserStatus.APPROVED.value)
    pending_user = create_test_user(db_session, "candidate@actia.com", role=UserRole.USER.value, status=UserStatus.PENDING.value)

    admin_token, _ = login_user(client, admin.email)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    user_token, _ = login_user(client, pending_user.email)
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # User initially blocked
    assert client.get("/api/v1/audits/", headers=user_headers).status_code == 403

    # Admin checks stats
    stats_resp = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["pending_users"] >= 1

    # Admin lists pending users
    list_resp = client.get("/api/v1/admin/users?status=PENDING", headers=admin_headers)
    assert list_resp.status_code == 200
    pending_list = list_resp.json()
    assert any(u["id"] == pending_user.id for u in pending_list)

    # Admin approves user
    approve_resp = client.patch(f"/api/v1/admin/users/{pending_user.id}/approve", headers=admin_headers)
    assert approve_resp.status_code == 200
    approved_data = approve_resp.json()
    assert approved_data["status"] == "APPROVED"
    assert approved_data["reviewed_by"] == admin.id
    assert approved_data["reviewed_at"] is not None

    # User now has access!
    after_resp = client.get("/api/v1/audits/", headers=user_headers)
    assert after_resp.status_code == 200


def test_admin_rejection_workflow(client, db_session):
    admin = create_test_user(db_session, "admin_reviewer@actia.com", role=UserRole.ADMIN.value, status=UserStatus.APPROVED.value)
    candidate = create_test_user(db_session, "bad_candidate@actia.com", role=UserRole.USER.value, status=UserStatus.PENDING.value)

    admin_token, _ = login_user(client, admin.email)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Reject without reason should fail validation
    invalid_reject = client.patch(f"/api/v1/admin/users/{candidate.id}/reject", json={}, headers=admin_headers)
    assert invalid_reject.status_code == 422

    # Reject with reason
    reason = "Adresse e-mail non rattachée à l'usine ACTIA."
    reject_resp = client.patch(
        f"/api/v1/admin/users/{candidate.id}/reject",
        json={"rejection_reason": reason},
        headers=admin_headers
    )
    assert reject_resp.status_code == 200
    rejected_data = reject_resp.json()
    assert rejected_data["status"] == "REJECTED"
    assert rejected_data["rejection_reason"] == reason
    assert rejected_data["reviewed_by"] == admin.id


def test_admin_suspend_user(client, db_session):
    admin = create_test_user(db_session, "admin_police@actia.com", role=UserRole.ADMIN.value, status=UserStatus.APPROVED.value)
    user = create_test_user(db_session, "troublemaker@actia.com", role=UserRole.USER.value, status=UserStatus.APPROVED.value)

    admin_token, _ = login_user(client, admin.email)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    user_token, _ = login_user(client, user.email)
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # User is initially approved
    assert client.get("/api/v1/audits/", headers=user_headers).status_code == 200

    # Admin suspends user
    suspend_resp = client.patch(f"/api/v1/admin/users/{user.id}/suspend", headers=admin_headers)
    assert suspend_resp.status_code == 200
    assert suspend_resp.json()["status"] == "SUSPENDED"

    # User is now rejected by session revocation and status guard
    blocked_resp = client.get("/api/v1/audits/", headers=user_headers)
    assert blocked_resp.status_code in [401, 403]
