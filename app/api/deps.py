"""
===============================================================================
DÉPENDANCES FASTAPI ET SÉCURITÉ DES REQUÊTES (DEPS.PY)
===============================================================================
Rôle :
  Fournit les fonctions d'injection de dépendances (Dependency Injection) FastAPI :
  1. `get_db` : Fournit une session de base de données SQLAlchemy par requête HTTP
     avec garantie de fermeture automatique (`finally: db.close()`).
  2. `oauth2_scheme` : Extrait automatiquement le token JWT depuis l'en-tête
     HTTP standard `Authorization: Bearer <token>`.
  3. `get_current_user` : Valide cryptographiquement le JWT, vérifie que la session
     n'a pas été révoquée (via l'identifiant JTI dans `user_session`), s'assure
     que le compte est actif et renvoie l'objet `User` authentifié.

Équipe de maintenance :
  - Pour protéger un nouvel endpoint dans un router FastAPI, ajoutez simplement :
    `current_user: User = Depends(get_current_user)` dans la signature de fonction.
===============================================================================
"""

from typing import Generator
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User, UserSession, UserRole, UserStatus
from app.schemas.user import TokenData

# Configuration du schéma OAuth2 standard indiquant à Swagger l'URL d'obtention du token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session de base de données transactionnelle pour chaque requête HTTP.
    
    Yields:
        Session: Instance de session SQLAlchemy active.
    
    Note:
        Le bloc `finally` garantit la clôture systématique de la session,
        évitant toute fuite de connexion dans le pool de PostgreSQL.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dépendance de sécurité principale : authentifie l'utilisateur porteur du jeton Bearer JWT.

    Args:
        db (Session): Session BDD injectée par get_db.
        token (str): Jeton JWT extrait du header Authorization par oauth2_scheme.

    Raises:
        HTTPException(401): Si le jeton est invalide, expiré ou si la session a été révoquée.
        HTTPException(400): Si le compte utilisateur est désactivé.

    Returns:
        User: Entité utilisateur SQLAlchemy authentifiée et active.
    """
    # Exception standard levée en cas d'échec d'authentification
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou jeton expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Décodage et vérification de la signature cryptographique du JWT
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")  # L'adresse email est stockée dans le sujet (sub)
        jti: str = payload.get("jti")    # Identifiant unique du jeton (JTI)
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Vérification de révocation dans la table des sessions actives (Déconnexion côté serveur)
    if jti:
        active_session = db.query(UserSession).filter(
            UserSession.access_jti == jti,
            UserSession.is_active == True
        ).first()
        if not active_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="La session a été révoquée ou est expirée (utilisateur déconnecté).",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Récupération du profil utilisateur en base de données
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    # Contrôle du statut d'activité du compte utilisateur
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte utilisateur est inactif ou désactivé."
        )

    return user


def get_current_approved_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dépendance de sécurité (Status Guard) :
    Exige que le compte utilisateur soit approuvé (status = 'APPROVED').
    Rejette toute requête avec HTTP 403 Forbidden si le compte est PENDING, REJECTED ou SUSPENDED.
    """
    if current_user.status != UserStatus.APPROVED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Accès refusé. Le statut de votre compte est : {current_user.status}."
        )
    return current_user


def require_admin(
    current_user: User = Depends(get_current_approved_user)
) -> User:
    """
    Dépendance de sécurité (Role Guard) :
    Exige que l'utilisateur possède le rôle administrateur (role = 'ADMIN').
    Rejette toute requête avec HTTP 403 Forbidden si l'utilisateur n'est pas administrateur.
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé. Privilèges administrateur requis."
        )
    return current_user

