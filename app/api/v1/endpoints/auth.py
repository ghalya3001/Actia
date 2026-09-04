import logging
import jwt
from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, oauth2_scheme
from app.core.config import settings
from app.core.email import send_otp_email
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    generate_otp_code,
)
from app.models.user import User, PasswordResetToken, RefreshToken, TokenBlacklist
from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
    RefreshTokenRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
    MsgResponse,
    OTPResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register a new Manager account")
def register_manager(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new Manager user account.
    Validates email uniqueness and hashes the password securely.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token, summary="Manager login for OAuth2 JWT token & Refresh Token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login. Accepts username (email) and password.
    Returns JWT access_token and refresh_token.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    access_token, jti, exp_at = create_access_token(subject=user.email)
    raw_refresh_token, ref_expires_at = generate_refresh_token()

    ref_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_password(raw_refresh_token),
        expires_at=ref_expires_at,
        is_revoked=False
    )
    db.add(ref_record)
    db.commit()

    return Token(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer"
    )


@router.post("/refresh-token", response_model=Token, summary="Get new Access Token using Refresh Token")
def refresh_token(
    body: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Exchange a valid Refresh Token for a fresh Access Token and new Refresh Token.
    """
    now = datetime.now(timezone.utc)
    active_refresh_tokens = db.query(RefreshToken).filter(
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > now
    ).all()

    target_record = None
    for rec in active_refresh_tokens:
        if verify_password(body.refresh_token, rec.token_hash):
            target_record = rec
            break

    if not target_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == target_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled or missing"
        )

    target_record.is_revoked = True

    new_access_token, jti, exp_at = create_access_token(subject=user.email)
    new_raw_refresh, new_ref_exp = generate_refresh_token()

    new_ref_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_password(new_raw_refresh),
        expires_at=new_ref_exp,
        is_revoked=False
    )
    db.add(new_ref_record)
    db.commit()

    return Token(
        access_token=new_access_token,
        refresh_token=new_raw_refresh,
        token_type="bearer"
    )


@router.post("/logout", response_model=MsgResponse, summary="Logout user and revoke current JWT token")
def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Any:
    """
    Revoke current JWT access token (add to blacklist) and revoke active refresh tokens for user.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc) + timedelta(minutes=60)
        
        if jti:
            blacklist_entry = TokenBlacklist(jti=jti, expires_at=expires_at)
            db.add(blacklist_entry)
    except Exception:
        pass

    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).update({"is_revoked": True})
    db.commit()

    return MsgResponse(message="Successfully logged out.")


@router.post("/change-password", response_model=MsgResponse, summary="Change password for authenticated Manager")
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change password for the currently logged-in Manager. Requires old password verification.
    """
    if not verify_password(body.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password."
        )

    current_user.hashed_password = hash_password(body.new_password)
    db.commit()

    return MsgResponse(message="Password updated successfully.")


@router.get("/me", response_model=UserResponse, summary="Get current logged-in Manager profile")
def read_current_user(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Fetch profile of the currently authenticated Manager.
    """
    return current_user


@router.post("/forgot-password", response_model=OTPResponse, summary="Generate 6-digit OTP code (returned directly in response)")
def forgot_password(
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Generates a 6-digit verification code (15 min expiration).
    Returns the OTP code directly in the response (no SMTP/email required).
    The UI displays this code to the user in a styled dialog.
    """
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not user.is_active:
        # Return generic message without revealing whether email exists
        return OTPResponse(
            message="If the email address exists in our system, a 6-digit verification code has been generated.",
            otp_code=None
        )

    otp_code = generate_otp_code()
    otp_hash = hash_password(otp_code)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)

    reset_record = PasswordResetToken(
        user_id=user.id,
        email=user.email,
        otp_code_hash=otp_hash,
        expires_at=expires_at,
        is_verified=False,
        is_used=False
    )
    db.add(reset_record)
    db.commit()

    # Log to console as well
    print(f"\n[OTP GENERATED] Code for {user.email}: {otp_code} (valid 15 min)\n")

    return OTPResponse(
        message="Votre code de vérification a été généré avec succès. Utilisez-le pour réinitialiser votre mot de passe.",
        otp_code=otp_code
    )


@router.post("/verify-otp", response_model=MsgResponse, summary="Verify 6-digit OTP code")
def verify_otp(
    body: VerifyOTPRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Validate 6-digit OTP code submitted by the user.
    """
    now = datetime.now(timezone.utc)
    active_otps = db.query(PasswordResetToken).filter(
        PasswordResetToken.email == body.email,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > now
    ).order_by(PasswordResetToken.id.desc()).all()

    target_otp_record = None
    for rec in active_otps:
        if verify_password(body.otp_code, rec.otp_code_hash):
            target_otp_record = rec
            break

    if not target_otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired 6-digit verification code."
        )

    target_otp_record.is_verified = True
    db.commit()

    return MsgResponse(message="Verification code validated successfully. You can now reset your password.")


@router.post("/reset-password", response_model=MsgResponse, summary="Reset password with verified 6-digit OTP code")
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Validate 6-digit OTP code and update user's password securely.
    """
    now = datetime.now(timezone.utc)
    active_otps = db.query(PasswordResetToken).filter(
        PasswordResetToken.email == body.email,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > now
    ).order_by(PasswordResetToken.id.desc()).all()

    target_otp_record = None
    for rec in active_otps:
        if verify_password(body.otp_code, rec.otp_code_hash):
            target_otp_record = rec
            break

    if not target_otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code."
        )

    user = db.query(User).filter(User.id == target_otp_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    user.hashed_password = hash_password(body.new_password)
    target_otp_record.is_used = True
    db.commit()

    return MsgResponse(message="Password has been reset successfully.")
