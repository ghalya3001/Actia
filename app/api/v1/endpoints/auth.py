"""
===============================================================================
ENDPOINTS D'AUTHENTIFICATION ET SÉCURITÉ DES COMPTES (AUTH.PY)
===============================================================================
Rôle :
  Gère l'ensemble du cycle de vie des utilisateurs et des sessions de connexion :
  1. `POST /register`        : Inscription d'un nouveau compte Manager avec hachage bcrypt.
  2. `POST /login`           : Connexion OAuth2 renvoyant Access Token (JWT) et Refresh Token.
  3. `POST /refresh-token`   : Rotation sécurisée du Refresh Token pour renouveler l'accès.
  4. `POST /logout`          : Révocation côté serveur du jeton et fermeture des sessions.
  5. `POST /change-password` : Changement de mot de passe pour un utilisateur authentifié.
  6. `GET  /me`              : Consultation des informations du profil connecté.
  7. Parcours OTP (3 étapes) :
     - `POST /forgot-password` : Génération du code OTP à 6 chiffres (valide 15 min).
     - `POST /verify-otp`      : Contrôle de la validité du code OTP soumis.
     - `POST /reset-password`   : Réinitialisation finale du mot de passe avec le code vérifié.

Équipe de maintenance :
  - La rotation des Refresh Tokens invalide l'ancien jeton dès qu'un nouveau est émis.
  - Les codes OTP sont hachés avec bcrypt dans la table `pwd_reset_request`.
===============================================================================
"""

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
from app.models.user import User, UserSession, PwdResetRequest
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


# =============================================================================
# 1. INSCRIPTION D'UN COMPTE MANAGER
# =============================================================================
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouveau compte Responsable HSE"
)
def register_manager(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Enregistre un nouveau compte utilisateur dans la table 'users'.
    Vérifie l'unicité de l'adresse e-mail et applique le hachage sécurisé bcrypt.

    Args:
        user_in (UserCreate): Données saisies (email, full_name, password).
        db (Session): Session BDD active.

    Raises:
        HTTPException(400): Si un compte avec cette adresse email existe déjà.

    Returns:
        User: L'enregistrement créé (le mot de passe haché est masqué par UserResponse).
    """
    # Vérification si l'adresse email est déjà utilisée
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    
    # Création de l'entité avec hachage bcrypt immédiat du mot de passe
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


# =============================================================================
# 2. CONNEXION ET OBTENTION DU JETON (LOGIN)
# =============================================================================
@router.post(
    "/login",
    response_model=Token,
    summary="Connexion utilisateur pour obtention du jeton JWT et Refresh Token"
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Point d'entrée conforme à la spécification OAuth2 Password Flow.
    Reçoit 'username' (qui correspond à l'email) et 'password'.

    Returns:
        Token: Paire de jetons (access_token signé avec jti, refresh_token opaque).
    """
    # Recherche de l'utilisateur par son adresse e-mail
    user = db.query(User).filter(User.email == form_data.username).first()

    # Vérification conjointe de l'existence et du mot de passe (évite la divulgation d'utilisateurs)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Adresse e-mail ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérification que le compte n'est pas suspendu
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte utilisateur est inactif"
        )
    
    # Génération du jeton d'accès court terme (60 min)
    access_token, jti, exp_at = create_access_token(subject=user.email)

    # Génération du jeton de rafraîchissement long terme (7 jours)
    raw_refresh_token, ref_expires_at = generate_refresh_token()

    # Enregistrement de la session dans 'user_session' avec hachage du Refresh Token
    session_record = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_password(raw_refresh_token),
        access_jti=jti,
        is_active=True,
        expires_at=ref_expires_at,
    )
    db.add(session_record)
    db.commit()

    return Token(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer"
    )


# =============================================================================
# 3. RENOUVELLEMENT DE JETON (REFRESH TOKEN ROTATION)
# =============================================================================
@router.post(
    "/refresh-token",
    response_model=Token,
    summary="Renouvellement de l'Access Token via le Refresh Token"
)
def refresh_token(
    body: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Échange un Refresh Token valide contre un nouvel Access Token et un nouveau Refresh Token.
    L'ancien Refresh Token est immédiatement révoqué (principe de rotation stricte).
    """
    now = datetime.now(timezone.utc)

    # Recherche parmi les sessions actives non expirées
    active_sessions = db.query(UserSession).filter(
        UserSession.is_active == True,
        UserSession.expires_at > now
    ).all()

    # Comparaison de l'empreinte pour identifier la session concernée
    target_session = None
    for s in active_sessions:
        if s.refresh_token_hash and verify_password(body.refresh_token, s.refresh_token_hash):
            target_session = s
            break

    if not target_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton de rafraîchissement invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Récupération et vérification du compte utilisateur
    user = db.query(User).filter(User.id == target_session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le compte utilisateur associé est désactivé ou introuvable"
        )

    # Révocation de l'ancienne session
    target_session.is_active = False

    # Émission d'une nouvelle paire de jetons (Rotation)
    new_access_token, jti, exp_at = create_access_token(subject=user.email)
    new_raw_refresh, new_ref_exp = generate_refresh_token()

    # Sauvegarde de la nouvelle session active
    new_session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_password(new_raw_refresh),
        access_jti=jti,
        is_active=True,
        expires_at=new_ref_exp,
    )
    db.add(new_session)
    db.commit()

    return Token(
        access_token=new_access_token,
        refresh_token=new_raw_refresh,
        token_type="bearer"
    )


# =============================================================================
# 4. DÉCONNEXION UTILISATEUR (LOGOUT)
# =============================================================================
@router.post(
    "/logout",
    response_model=MsgResponse,
    summary="Déconnexion et révocation de la session côté serveur"
)
def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Any:
    """
    Révoque immédiatement le jeton d'accès courant (via son identifiant JTI)
    et désactive toutes les sessions actives de l'utilisateur.
    """
    # Désactivation ciblée de la session liée au JTI de ce jeton
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        if jti:
            db.query(UserSession).filter(UserSession.access_jti == jti).update({"is_active": False})
    except Exception:
        pass

    # Désactivation générale de toutes les sessions de cet utilisateur
    db.query(UserSession).filter(UserSession.user_id == current_user.id).update({"is_active": False})
    db.commit()

    return MsgResponse(message="Déconnexion effectuée avec succès.")


# =============================================================================
# 5. CHANGEMENT DE MOT DE PASSE (UTILISATEUR AUTHENTIFIÉ)
# =============================================================================
@router.post(
    "/change-password",
    response_model=MsgResponse,
    summary="Changement du mot de passe par le manager connecté"
)
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Permet à un manager authentifié de remplacer son mot de passe.
    Exige la saisie et validation de l'ancien mot de passe actuel.
    """
    if not verify_password(body.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'ancien mot de passe saisi est incorrect."
        )

    # Hachage et enregistrement du nouveau mot de passe
    current_user.hashed_password = hash_password(body.new_password)
    db.commit()

    return MsgResponse(message="Mot de passe mis à jour avec succès.")


# =============================================================================
# 6. CONSULTATION DU PROFIL UTILISATEUR ACTUEL
# =============================================================================
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Récupération du profil du manager connecté"
)
def read_current_user(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retourne l'identité du manager connecté (nom, email, statut actif, date d'inscription).
    """
    return current_user


# =============================================================================
# 7. PARCOURS DE RÉINITIALISATION DE MOT DE PASSE PAR OTP (3 ÉTAPES)
# =============================================================================
@router.post(
    "/forgot-password",
    response_model=OTPResponse,
    summary="Étape 1 : Demande de code OTP pour réinitialisation de mot de passe"
)
def forgot_password(
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Génère un code numérique à 6 chiffres à durée limitée (15 minutes).
    Stocke l'empreinte bcrypt du code dans 'pwd_reset_request'.
    Retourne le code directement pour une prise en charge immédiate par l'interface.
    """
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not user.is_active:
        # Réponse générique pour ne pas révéler si l'email existe dans la BDD
        return OTPResponse(
            message="Si cette adresse e-mail existe dans notre système, un code à 6 chiffres a été généré.",
            otp_code=None
        )

    # Génération du code à 6 chiffres
    otp_code = generate_otp_code()
    otp_hash = hash_password(otp_code)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)

    # Enregistrement de la demande en base
    reset_record = PwdResetRequest(
        user_id=user.id,
        email=user.email,
        otp_hash=otp_hash,
        expires_at=expires_at,
        is_used=False
    )
    db.add(reset_record)
    db.commit()

    # Envoi éventuel par e-mail si SMTP configuré
    send_otp_email(user.email, otp_code)

    # Trace en console pour le débogage et tests
    print(f"\n[OTP GENERATED] Code pour {user.email} : {otp_code} (valide 15 minutes)\n")

    return OTPResponse(
        message="Votre code de vérification a été généré avec succès. Utilisez-le pour réinitialiser votre mot de passe.",
        otp_code=otp_code
    )


@router.post(
    "/verify-otp",
    response_model=MsgResponse,
    summary="Étape 2 : Vérification de la conformité du code OTP à 6 chiffres"
)
def verify_otp(
    body: VerifyOTPRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Contrôle si le code à 6 chiffres saisi correspond à une demande active et non expirée.
    """
    now = datetime.now(timezone.utc)
    active_otps = db.query(PwdResetRequest).filter(
        PwdResetRequest.email == body.email,
        PwdResetRequest.is_used == False,
        PwdResetRequest.expires_at > now
    ).order_by(PwdResetRequest.id.desc()).all()

    target_otp_record = None
    for rec in active_otps:
        if verify_password(body.otp_code, rec.otp_hash):
            target_otp_record = rec
            break

    if not target_otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de vérification à 6 chiffres invalide ou expiré."
        )

    return MsgResponse(message="Code de vérification validé avec succès. Vous pouvez maintenant définir un nouveau mot de passe.")


@router.post(
    "/reset-password",
    response_model=MsgResponse,
    summary="Étape 3 : Définition définitive du nouveau mot de passe avec le code OTP validé"
)
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Valide le code OTP une dernière fois, met à jour le mot de passe de l'utilisateur
    et marque la demande comme consommée (is_used = True).
    """
    now = datetime.now(timezone.utc)
    active_otps = db.query(PwdResetRequest).filter(
        PwdResetRequest.email == body.email,
        PwdResetRequest.is_used == False,
        PwdResetRequest.expires_at > now
    ).order_by(PwdResetRequest.id.desc()).all()

    target_otp_record = None
    for rec in active_otps:
        if verify_password(body.otp_code, rec.otp_hash):
            target_otp_record = rec
            break

    if not target_otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de vérification invalide ou expiré."
        )

    # Récupération du compte utilisateur associé
    user = db.query(User).filter(User.id == target_otp_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    # Mise à jour sécurisée du mot de passe
    user.hashed_password = hash_password(body.new_password)

    # Marquage de la demande comme utilisée (invalide pour toute future tentative)
    target_otp_record.is_used = True
    db.commit()

    return MsgResponse(message="Votre mot de passe a été réinitialisé avec succès.")
