"""
===============================================================================
SCHÉMAS DE VALIDATION PYDANTIC — DOMAINE UTILISATEUR & AUTH (USER.PY)
===============================================================================
Rôle :
  Définit les règles de validation et de typage strict pour toutes les opérations
  liées aux comptes utilisateurs, aux jetons d'authentification et à la sécurité :
  - Création de compte (UserCreate) avec contrôle de complexité du mot de passe.
  - Restitution du profil (UserResponse) excluant strictement le mot de passe.
  - Modèles de jetons JWT et Refresh Tokens (Token, RefreshTokenRequest).
  - Parcours de réinitialisation de mot de passe par code OTP (ForgotPasswordRequest,
    VerifyOTPRequest, ResetPasswordRequest).

Équipe de maintenance :
  - Pydantic valide automatiquement les formats (ex: EmailStr rejette les adresses malformées).
  - Les attributs `min_length` protègent l'application contre les mots de passe trop courts.
===============================================================================
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


# =============================================================================
# 1. SCHÉMAS DE BASE ET CRÉATION DE COMPTE
# =============================================================================
class UserBase(BaseModel):
    """
    Champs fondamentaux partagés par toutes les représentations d'un utilisateur.
    """
    # Adresse e-mail obligatoire et validée selon la norme RFC 5322
    email: EmailStr

    # Nom et prénom du manager (longueur comprise entre 2 et 100 caractères)
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """
    Schéma de payload reçu lors de l'enregistrement d'un nouveau Manager.
    """
    # Mot de passe en clair exigeant au minimum 8 caractères
    password: str = Field(..., min_length=8, description="Le mot de passe doit comporter au moins 8 caractères")


class UserResponse(UserBase):
    """
    Schéma de réponse public retourné par l'API (ex: /api/v1/auth/me).
    Ne contient JAMAIS le mot de passe ni son empreinte de hachage.
    """
    id: int
    is_active: bool
    created_at: datetime

    # Permet à Pydantic de lire directement les attributs d'une instance ORM SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# 2. SCHÉMAS DES JETONS D'AUTHENTIFICATION (JWT)
# =============================================================================
class Token(BaseModel):
    """
    Réponse renvoyée après une authentification réussie (/login ou /refresh).
    """
    access_token: str                  # Jeton JWT d'accès court terme (60 minutes)
    refresh_token: Optional[str] = None # Jeton de rafraîchissement long terme (7 jours)
    token_type: str = "bearer"         # Type d'autorisation standard HTTP Bearer


class TokenData(BaseModel):
    """
    Données internes extraites du décodage du payload d'un jeton JWT.
    """
    email: Optional[str] = None        # Adresse e-mail de l'utilisateur (subject)
    jti: Optional[str] = None          # Identifiant unique du jeton pour validation/révocation


class RefreshTokenRequest(BaseModel):
    """
    Requête envoyée pour obtenir un nouvel Access Token à partir d'un Refresh Token.
    """
    refresh_token: str                 # Jeton opaque débutant généralement par 'ref_'


# =============================================================================
# 3. SCHÉMAS DE MODIFICATION ET RÉINITIALISATION DE MOT DE PASSE (OTP)
# =============================================================================
class ChangePasswordRequest(BaseModel):
    """
    Requête soumise par un utilisateur connecté souhaitant changer son mot de passe.
    """
    old_password: str                  # Ancien mot de passe actuel pour vérification
    new_password: str = Field(..., min_length=8, description="Le nouveau mot de passe doit comporter au moins 8 caractères")


class ForgotPasswordRequest(BaseModel):
    """
    Étape 1 : Demande d'envoi du code OTP suite à l'oubli du mot de passe.
    """
    email: EmailStr                    # Adresse e-mail du compte à débloquer


class VerifyOTPRequest(BaseModel):
    """
    Étape 2 : Vérification de la conformité du code à 6 chiffres reçu par e-mail.
    """
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, description="Code de vérification numérique à 6 chiffres")


class ResetPasswordRequest(BaseModel):
    """
    Étape 3 : Application définitive du nouveau mot de passe avec validation du code OTP.
    """
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, description="Code de vérification numérique à 6 chiffres")
    new_password: str = Field(..., min_length=8, description="Le nouveau mot de passe doit comporter au moins 8 caractères")


# =============================================================================
# 4. SCHÉMAS DE RÉPONSES GÉNÉRIQUES
# =============================================================================
class MsgResponse(BaseModel):
    """
    Message de confirmation générique au format JSON standard.
    """
    message: str


class OTPResponse(BaseModel):
    """
    Réponse renvoyée lors de l'émission d'un code OTP.
    En mode simulation locale, le champ 'otp_code' peut être renseigné directement.
    """
    message: str
    otp_code: Optional[str] = None
