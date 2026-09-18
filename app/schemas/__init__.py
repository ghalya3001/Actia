"""
===============================================================================
CATALOGUE DES SCHÉMAS PYDANTIC (__INIT__.PY)
===============================================================================
Rôle :
  Exporte et centralise tous les schémas de validation Pydantic de l'application.
  Ces schémas (Data Transfer Objects - DTOs) définissent la structure des données
  échangées entre le client (Frontend Vue 3) et l'API FastAPI :
  - Validation automatique des requêtes entrantes (Body, JSON, formulaires).
  - Sérialisation et filtrage des réponses sortantes (masquage des mots de passe).
===============================================================================
"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    Token,
    TokenData,
    RefreshTokenRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
    MsgResponse,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "Token",
    "TokenData",
    "RefreshTokenRequest",
    "ChangePasswordRequest",
    "ForgotPasswordRequest",
    "VerifyOTPRequest",
    "ResetPasswordRequest",
    "MsgResponse",
]
