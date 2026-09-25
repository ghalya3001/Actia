"""
===============================================================================
MODÈLES DE DONNÉES — DOMAINE UTILISATEUR ET SÉCURITÉ (USER.PY)
===============================================================================
Rôle :
  Implémente l'architecture 3 tables pour la gestion des comptes et de la sécurité :
  1. `User` : Comptes des Managers HSE (informations d'identité, mot de passe haché).
  2. `UserSession` : Sessions actives, jetons de rafraîchissement (Refresh Tokens)
     et traçabilité des accès pour permettre la révocation ou la déconnexion distante.
  3. `PwdResetRequest` : Demandes sécurisées de réinitialisation de mot de passe avec
     hachage du code OTP à 6 chiffres et horodatage de validité (15 minutes).

Équipe de maintenance :
  - Toutes les relations enfant utilisent `ondelete="CASCADE"` et `cascade="all, delete-orphan"` :
    si un utilisateur est supprimé, ses sessions, demandes OTP et soumissions sont nettoyées.
  - Les mots de passe et codes OTP ne sont JAMAIS stockés en clair (toujours hachés via bcrypt).
===============================================================================
"""

import enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.db.base import Base


# =============================================================================
# ENUMS : RÔLES & STATUTS DU CYCLE DE VIE DES COMPTES
# =============================================================================
class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


# =============================================================================
# 1. TABLE PRINCIPALE : USERS (Comptes Utilisateurs / Managers)
# =============================================================================
class User(Base):
    """
    Entité représentant un utilisateur ou responsable de la plateforme HSE.
    Gère les rôles RBAC (USER, ADMIN) et le cycle de validation (PENDING, APPROVED, REJECTED, SUSPENDED).
    """
    __tablename__ = "users"

    # Clé primaire auto-incrémentée
    id = Column(Integer, primary_key=True, index=True)

    # Nom et prénom complets du manager (ex: 'Ghalyya Mimouna')
    full_name = Column(String(255), nullable=False)

    # Adresse e-mail unique servant d'identifiant de connexion
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Empreinte hachée bcrypt du mot de passe (jamais en clair)
    hashed_password = Column(String(255), nullable=False)

    # Rôle RBAC : USER ou ADMIN (extensible)
    role = Column(String(50), default=UserRole.USER.value, nullable=False, index=True)

    # Statut du compte : PENDING, APPROVED, REJECTED, SUSPENDED
    status = Column(String(50), default=UserStatus.PENDING.value, nullable=False, index=True)

    # Motif du rejet si le compte est rejeté
    rejection_reason = Column(Text, nullable=True)

    # Référence vers l'administrateur ayant approuvé/rejeté/suspendu ce compte
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Date et heure de la revue du compte
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Indicateur d'activation du compte (False bloque toute tentative de connexion)
    is_active = Column(Boolean, default=True)

    # Date et heure de création du compte (horodatée automatiquement par PostgreSQL)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- Relations ORM (1 utilisateur vers N entités dépendantes) ---
    # Administrateur ayant validé ce compte
    reviewer = relationship("User", remote_side=[id], foreign_keys=[reviewed_by])

    @property
    def reviewer_name(self) -> Optional[str]:
        return self.reviewer.full_name if self.reviewer else None

    @property
    def reviewer_email(self) -> Optional[str]:
        return self.reviewer.email if self.reviewer else None

    # Sessions de connexion associées à l'utilisateur
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan", foreign_keys="UserSession.user_id")

    # Demandes de réinitialisation de mot de passe par code OTP
    pwd_reset_requests = relationship("PwdResetRequest", back_populates="user", cascade="all, delete-orphan")

    # Formulaires HSE soumis par ce manager (Audits, Tournées, Permis)
    submissions = relationship("FormSubmission", back_populates="user", cascade="all, delete-orphan")

    # Instantanés de KPI calculés et enregistrés pour cet utilisateur
    kpi_snapshots = relationship("KPISnapshot", back_populates="user", cascade="all, delete-orphan")

    # Widgets et préférences d'agencement du tableau de bord
    dashboard_widgets = relationship("DashboardWidget", back_populates="user", cascade="all, delete-orphan")


# =============================================================================
# 2. TABLE DES SESSIONS : USER_SESSION (Gestion des Refresh Tokens & Déconnexions)
# =============================================================================
class UserSession(Base):
    """
    Représente une session active liée à un Refresh Token.
    Permet la rotation sécurisée des jetons et la révocation unitaire lors de la déconnexion.
    """
    __tablename__ = "user_session"

    # Clé primaire de la session
    id = Column(Integer, primary_key=True, index=True)

    # Clé étrangère vers l'utilisateur propriétaire du jeton
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Empreinte hachée du Refresh Token (évite le vol de jetons en cas de dump BDD)
    refresh_token_hash = Column(String(255), index=True, nullable=True)

    # Identifiant unique JTI (JWT ID) associé au dernier Access Token émis
    access_jti = Column(String(255), index=True, nullable=True)

    # Statut de la session : False si le manager s'est déconnecté (jeton révoqué)
    is_active = Column(Boolean, default=True, nullable=False)

    # Date limite de validité du Refresh Token (typiquement +7 jours)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Date de création de la session
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Horodatage du dernier rafraîchissement d'accès
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    # Relation inverse vers le modèle User
    user = relationship("User", back_populates="sessions")


# =============================================================================
# 3. TABLE DES DEMANDES DE RÉINITIALISATION : PWD_RESET_REQUEST (Codes OTP)
# =============================================================================
class PwdResetRequest(Base):
    """
    Stocke les demandes de réinitialisation de mot de passe par code OTP à 6 chiffres.
    Garantit une sécurité maximale grâce au hachage du code OTP et au contrôle d'expiration.
    """
    __tablename__ = "pwd_reset_request"

    # Clé primaire de la demande
    id = Column(Integer, primary_key=True, index=True)

    # Référence de l'utilisateur concerné
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Adresse e-mail destinataire pour vérification croisée
    email = Column(String(255), index=True, nullable=False)

    # Empreinte hachée bcrypt du code OTP à 6 chiffres (le code en clair n'est jamais stocké)
    otp_hash = Column(String(255), nullable=False)

    # Date d'expiration stricte du code (15 minutes après génération)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Indicateur d'utilisation : passe à True dès que le mot de passe est réinitialisé
    is_used = Column(Boolean, default=False, nullable=False)

    # Horodatage de création de la demande
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relation inverse vers le modèle User
    user = relationship("User", back_populates="pwd_reset_requests")
