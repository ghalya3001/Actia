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
  - Modèle historique d'audit : HSEAudit
  - Formulaires et Contrôles terrain : FormSubmission, AuditHSESubmission,
    AuditHSEItem, TourneeHSESubmission, TourneeHSEItem, PermisTravailSubmission,
    PhotoStorage, AccidentTravailSubmission, AccidentTravailMonthlyItem
  - Pilotage et Dashboard : KPIDefinition, KPISnapshot, DashboardWidget
===============================================================================
"""

from app.models.user import User, UserSession, PwdResetRequest
from app.models.audit import HSEAudit
from app.models.submission import (
    FormSubmission,
    AuditHSESubmission,
    AuditHSEItem,
    TourneeHSESubmission,
    TourneeHSEItem,
    PermisTravailSubmission,
    PhotoStorage,
    AccidentTravailSubmission,
    AccidentTravailMonthlyItem,
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
    "HSEAudit",
    "FormSubmission",
    "AuditHSESubmission",
    "AuditHSEItem",
    "TourneeHSESubmission",
    "TourneeHSEItem",
    "PermisTravailSubmission",
    "PhotoStorage",
    "AccidentTravailSubmission",
    "AccidentTravailMonthlyItem",
    "KPIDefinition",
    "KPISnapshot",
    "DashboardWidget",
]
