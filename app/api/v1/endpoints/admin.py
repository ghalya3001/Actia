"""
===============================================================================
ENDPOINTS D'ADMINISTRATION & GESTION DES UTILISATEURS (ADMIN.PY)
===============================================================================
Rôle :
  Expose l'ensemble des opérations d'administration pour la gestion des utilisateurs,
  l'approbation des comptes, le rejet et la suspension (RBAC) :
  - `GET   /stats`             : Statistiques globales sur les comptes utilisateurs.
  - `GET   /users`             : Liste filtrable (par statut, rôle, recherche textuelle).
  - `GET   /users/{id}`        : Consultation des détails complets d'un compte.
  - `PATCH /users/{id}/approve`: Approbation d'un compte (passe à 'APPROVED').
  - `PATCH /users/{id}/reject` : Rejet d'un compte avec motif obligatoire (passe à 'REJECTED').
  - `PATCH /users/{id}/suspend`: Suspension d'un compte et révocation immédiate de ses sessions.

Sécurité :
  - Toutes les routes de ce module exigent le rôle administrateur (`Depends(require_admin)`).
===============================================================================
"""

from typing import List, Optional, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.api.deps import get_db, require_admin
from app.models.user import User, UserSession, UserRole, UserStatus
from app.schemas.user import (
    AdminUserOut,
    AdminStatsOut,
    RejectUserRequest,
    UpdateUserRoleRequest,
    MsgResponse,
)

router = APIRouter()


# =============================================================================
# 1. STATISTIQUES GLOBALES DES UTILISATEURS
# =============================================================================
@router.get(
    "/stats",
    response_model=AdminStatsOut,
    summary="Obtenir les compteurs d'utilisateurs par statut"
)
def get_user_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    """
    Retourne les totaux d'utilisateurs par statut pour le bandeau supérieur de l'espace admin.
    """
    total = db.query(User).count()
    pending = db.query(User).filter(User.status == UserStatus.PENDING.value).count()
    approved = db.query(User).filter(User.status == UserStatus.APPROVED.value).count()
    rejected = db.query(User).filter(User.status == UserStatus.REJECTED.value).count()
    suspended = db.query(User).filter(User.status == UserStatus.SUSPENDED.value).count()

    return AdminStatsOut(
        total_users=total,
        pending_users=pending,
        approved_users=approved,
        rejected_users=rejected,
        suspended_users=suspended
    )


# =============================================================================
# 2. LISTE FILTRABLE DES UTILISATEURS
# =============================================================================
@router.get(
    "/users",
    response_model=List[AdminUserOut],
    summary="Lister les utilisateurs avec filtres par statut, rôle ou recherche"
)
def list_users(
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrer par statut (PENDING, APPROVED, etc.)"),
    role_filter: Optional[str] = Query(None, alias="role", description="Filtrer par rôle (USER, ADMIN)"),
    search: Optional[str] = Query(None, description="Rechercher par nom ou adresse e-mail"),
    date_from: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    """
    Récupère la liste des utilisateurs enregistrés, triés par date de création descendante.
    Permet de filtrer par statut, rôle, recherche textuelle et plage de dates.
    Si seule date_from est fournie, filtre précisément sur cette journée.
    """
    query = db.query(User).options(joinedload(User.reviewer))

    if status_filter:
        query = query.filter(User.status == status_filter.upper())

    if role_filter:
        query = query.filter(User.role == role_filter.upper())

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )

    # Filtrage par plage de dates ou par date unique
    if date_from and date_to:
        try:
            start_dt = datetime.fromisoformat(date_from).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
            end_dt = datetime.fromisoformat(date_to).replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
            query = query.filter(User.created_at >= start_dt, User.created_at <= end_dt)
        except Exception:
            pass
    elif date_from:
        # Si seule la date de début est renseignée : filtre sur la journée entière de cette date
        try:
            start_dt = datetime.fromisoformat(date_from).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
            end_dt = datetime.fromisoformat(date_from).replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
            query = query.filter(User.created_at >= start_dt, User.created_at <= end_dt)
        except Exception:
            pass
    elif date_to:
        try:
            end_dt = datetime.fromisoformat(date_to).replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
            query = query.filter(User.created_at <= end_dt)
        except Exception:
            pass

    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


# =============================================================================
# 3. DÉTAILS D'UN UTILISATEUR SPÉCIFIQUE
# =============================================================================
@router.get(
    "/users/{user_id}",
    response_model=AdminUserOut,
    summary="Consulter les détails complets d'un compte utilisateur"
)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    """
    Récupère les informations détaillées d'un utilisateur par son ID.
    """
    user = db.query(User).options(joinedload(User.reviewer)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )
    return user


# =============================================================================
# 4. APPROBATION D'UN COMPTE UTILISATEUR
# =============================================================================
@router.patch(
    "/users/{user_id}/approve",
    response_model=AdminUserOut,
    summary="Approuver un compte utilisateur"
)
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    """
    Bascule le statut de l'utilisateur à 'APPROVED'.
    Enregistre l'administrateur ayant validé le compte et la date/heure de l'approbation.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    user.status = UserStatus.APPROVED.value
    user.rejection_reason = None
    user.reviewed_by = current_admin.id
    user.reviewed_at = datetime.now(timezone.utc)
    user.is_active = True

    db.commit()
    return db.query(User).options(joinedload(User.reviewer)).filter(User.id == user_id).first()


# =============================================================================
# 5. REJET D'UN COMPTE UTILISATEUR (AVEC MOTIF)
# =============================================================================
@router.patch(
    "/users/{user_id}/reject",
    response_model=AdminUserOut,
    summary="Rejeter un compte utilisateur avec motif obligatoire"
)
def reject_user(
    user_id: int,
    payload: RejectUserRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    """
    Bascule le statut de l'utilisateur à 'REJECTED' et consigne le motif de refus.
    Révoque immédiatement toutes ses sessions actives pour bloquer les accès.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    # Empêcher un admin de s'auto-rejeter
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas rejeter votre propre compte administrateur."
        )

    user.status = UserStatus.REJECTED.value
    user.rejection_reason = payload.rejection_reason
    user.reviewed_by = current_admin.id
    user.reviewed_at = datetime.now(timezone.utc)

    # Révocation des sessions actives
    db.query(UserSession).filter(UserSession.user_id == user.id).update({"is_active": False})

    db.commit()
    return db.query(User).options(joinedload(User.reviewer)).filter(User.id == user_id).first()


# =============================================================================
# 6. SUSPENSION D'UN COMPTE UTILISATEUR
# =============================================================================
@router.patch(
    "/users/{user_id}/suspend",
    response_model=AdminUserOut,
    summary="Suspendre un compte utilisateur"
)
def suspend_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    """
    Bascule le statut de l'utilisateur à 'SUSPENDED'.
    Révoque immédiatement toutes ses sessions de connexion actives.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    # Empêcher un admin de s'auto-suspendre
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas suspendre votre propre compte administrateur."
        )

    user.status = UserStatus.SUSPENDED.value
    user.reviewed_by = current_admin.id
    user.reviewed_at = datetime.now(timezone.utc)

    # Révocation immédiate de toutes les sessions actives
    db.query(UserSession).filter(UserSession.user_id == user.id).update({"is_active": False})

    db.commit()
    return db.query(User).options(joinedload(User.reviewer)).filter(User.id == user_id).first()


# =============================================================================
# 7. MODIFICATION DU RÔLE D'UN UTILISATEUR (OPTIONNEL)
# =============================================================================
@router.patch(
    "/users/{user_id}/role",
    response_model=AdminUserOut,
    summary="Changer le rôle d'un utilisateur (USER ou ADMIN)"
)
def update_user_role(
    user_id: int,
    payload: UpdateUserRoleRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    """
    Permet à un administrateur d'élever ou modifier le rôle d'un autre utilisateur.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    new_role = payload.role.upper()
    if new_role not in [UserRole.USER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rôle invalide. Rôles autorisés : {UserRole.USER.value}, {UserRole.ADMIN.value}"
        )

    # Empêcher de rétrograder le dernier admin ou soi-même
    if user.id == current_admin.id and new_role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas retirer vos propres privilèges administrateur."
        )

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user
