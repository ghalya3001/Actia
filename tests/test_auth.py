import pytest
from app.core.security import hash_password, verify_password, generate_otp_code
from app.models.user import PasswordResetToken

def test_password_hashing():
    pwd = "SecretPassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_register_manager(client):
    payload = {
        "email": "manager@platformactia.com",
        "full_name": "Manager One",
        "password": "SecurePassword123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert data["is_active"] is True
    assert "hashed_password" not in data

def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@platformactia.com",
        "full_name": "Manager Duplicate",
        "password": "SecurePassword123"
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"]

def test_login_success(client):
    reg_payload = {
        "email": "login@platformactia.com",
        "full_name": "Login Manager",
        "password": "MyPassword123"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_data = {
        "username": "login@platformactia.com",
        "password": "MyPassword123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_resp = response.json()
    assert "access_token" in token_resp
    assert "refresh_token" in token_resp
    assert token_resp["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    login_data = {
        "username": "nonexistent@platformactia.com",
        "password": "MyPassword123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401

def test_get_current_user_me(client):
    reg_payload = {
        "email": "me@platformactia.com",
        "full_name": "Profile Manager",
        "password": "MyPassword123"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "me@platformactia.com", "password": "MyPassword123"}
    )
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "me@platformactia.com"
    assert me_data["full_name"] == "Profile Manager"

def test_refresh_token_flow(client):
    reg_payload = {
        "email": "refresh@platformactia.com",
        "full_name": "Refresh Manager",
        "password": "MyPassword123"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@platformactia.com", "password": "MyPassword123"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    ref_resp = client.post("/api/v1/auth/refresh-token", json={"refresh_token": refresh_token})
    assert ref_resp.status_code == 200
    ref_data = ref_resp.json()
    assert "access_token" in ref_data
    assert "refresh_token" in ref_data

def test_logout_flow(client):
    reg_payload = {
        "email": "logout@platformactia.com",
        "full_name": "Logout Manager",
        "password": "MyPassword123"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "logout@platformactia.com", "password": "MyPassword123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

    logout_resp = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 200

    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401

def test_change_password_flow(client):
    reg_payload = {
        "email": "changepwd@platformactia.com",
        "full_name": "ChangePwd Manager",
        "password": "OldPassword123"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "changepwd@platformactia.com", "password": "OldPassword123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    change_resp = client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "OldPassword123", "new_password": "BrandNewPassword123!"},
        headers=headers
    )
    assert change_resp.status_code == 200

    new_login = client.post(
        "/api/v1/auth/login",
        data={"username": "changepwd@platformactia.com", "password": "BrandNewPassword123!"}
    )
    assert new_login.status_code == 200

def test_forgot_and_reset_password_otp_flow(client, db_session):
    # 1. Register User
    reg_payload = {
        "email": "forgot_otp@platformactia.com",
        "full_name": "Forgot OTP Manager",
        "password": "OldPassword123"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Trigger Forgot Password
    forgot_resp = client.post("/api/v1/auth/forgot-password", json={"email": "forgot_otp@platformactia.com"})
    assert forgot_resp.status_code == 200
    assert "verification code" in forgot_resp.json()["message"]

    # 3. Simulate OTP code for testing
    otp_code = "849201"
    token_record = db_session.query(PasswordResetToken).filter(PasswordResetToken.email == "forgot_otp@platformactia.com").first()
    assert token_record is not None
    token_record.otp_code_hash = hash_password(otp_code)
    db_session.commit()

    # 4. Verify OTP Code
    verify_resp = client.post("/api/v1/auth/verify-otp", json={"email": "forgot_otp@platformactia.com", "otp_code": otp_code})
    assert verify_resp.status_code == 200

    # 5. Reset Password
    reset_resp = client.post("/api/v1/auth/reset-password", json={
        "email": "forgot_otp@platformactia.com",
        "otp_code": otp_code,
        "new_password": "NewSuperPassword123!"
    })
    assert reset_resp.status_code == 200

    # 6. Login with New Password
    new_login = client.post("/api/v1/auth/login", data={"username": "forgot_otp@platformactia.com", "password": "NewSuperPassword123!"})
    assert new_login.status_code == 200
