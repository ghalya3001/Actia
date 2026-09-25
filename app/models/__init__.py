"""
===============================================================================
CATALOGUE GLOBAL DES MODÈLES ORM SQLALCHEMY (__INIT__.PY)
===============================================================================
Rôle :
  Exporte et centralise tous les modèles de données de l'application.
  Cet import permet à `Base.metadata` de découvrir l'ensemble des tables déclarées
  pour la création automatique des schémas PostgreSQL lors du démarrage du serveur
  (dans `app/main.py`) et pour les migrations éventuelles.

Modèles exposés :
  - Utilisateurs et Sécurité : User, UserSession, PwdResetRequest
  - Enums de domaine : UserRole, UserStatus, Conformite, EtatAction
  - Formulaires et Contrôles terrain : FormSubmission, AuditHSESubmission,
    AuditHSEItem, TourneeHSESubmission, TourneeHSEItem, PermisTravailSubmission,
    PhotoStorage, AccidentTravailSubmission, AccidentTravailMonthlyItem
  - Champs personnalisés : CustomFieldDefinition, CustomFieldValue
  - Pilotage et Dashboard : KPIDefinition, KPISnapshot, DashboardWidget
===============================================================================
"""

from app.models.user import User, UserSession, PwdResetRequest, UserRole, UserStatus
from app.models.submission import (
    Conformite,
    EtatAction,
    FormSubmission,
    AuditHSESubmission,
    AuditHSEItem,
    TourneeHSESubmission,
    TourneeHSEItem,
    PermisTravailSubmission,
    PhotoStorage,
    AccidentTravailSubmission,
    AccidentTravailMonthlyItem,
    CustomFieldDefinition,
    CustomFieldValue,
)
from app.models.dashboard import (
    KPIDefinition,
    KPISnapshot,
    DashboardWidget,
)

__all__ = [
    "User",
    "UserSession",
    "PwdResetRequest",
    "UserRole",
    "UserStatus",
    "Conformite",
    "EtatAction",
    "FormSubmission",
    "AuditHSESubmission",
    "AuditHSEItem",
    "TourneeHSESubmission",
    "TourneeHSEItem",
    "PermisTravailSubmission",
    "PhotoStorage",
    "AccidentTravailSubmission",
    "AccidentTravailMonthlyItem",
    "CustomFieldDefinition",
    "CustomFieldValue",
    "KPIDefinition",
    "KPISnapshot",
    "DashboardWidget",
]

