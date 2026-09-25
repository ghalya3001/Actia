"""
===============================================================================
SCHÉMAS DE VALIDATION PYDANTIC — DOMAINE AUDITS & SOUMISSIONS HSE (AUDIT.PY)
===============================================================================
Rôle :
  Définit les contrats de validation des requêtes et réponses pour la gestion
  des formulaires HSE (création, mise à jour, affichage unitaire et statistiques) :
  - `HSEAuditCreate` : Validation complète lors de la soumission d'une nouvelle fiche.
  - `HSEAuditUpdate` : Modification partielle (PATCH / PUT) d'un audit existant.
  - `HSEAuditOut` : Modèle de réponse renvoyé au frontend pour consultation.
  - `HSEAuditStats` : Agrégats statistiques pour les widgets du tableau de bord.

Équipe de maintenance :
  - `items_data` transporte la structure arborescente des questions avec constats,
    photos en base64/URL, responsables et échéances d'actions.
===============================================================================
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


# =============================================================================
# 1. SCHÉMA DE CRÉATION : HSEAUDITCREATE
# =============================================================================
class HSEAuditCreate(BaseModel):
    """
    Structure des données transmises par le frontend lors de la validation
    d'un nouveau formulaire (Audit HSE, Tournée HSE, Permis de Travail, etc.).
    """
    # Référence documentaire qualité (ex: 'FGSI-001-Ind:F')
    reference: str = Field(default="FGSI-001-Ind:F")

    # Identifiant du formulaire rempli ('audit_hse_complet', 'tournee_hse', etc.)
    form_type: str = Field(default="audit_hse_complet")

    # Zone géographique ou ligne de production de l'usine
    secteur: str

    # Liste ou noms des participants et auditeurs présents
    intervenants: str

    # Date de réalisation du contrôle (format ISO YYYY-MM-DD)
    date_audit: str

    # Synthèse ou remarques générales rédigées par l'auditeur
    commentaires_generaux: Optional[str] = None

    # Indicateurs statistiques calculés automatiquement par l'assistant (Wizard)
    taux_conformite: float = 0.0
    total_conforme: int = 0
    total_non_conforme: int = 0
    total_na: int = 0

    # Compteurs de répartition des statuts d'actions correctives
    count_soldee: int = 0
    count_non_engagee: int = 0
    count_en_cours: int = 0
    count_en_retard: int = 0

    # Arborescence complète des points de contrôle, questions, constats et photos
    items_data: Dict[str, Any]


# =============================================================================
# 2. SCHÉMA DE MISE À JOUR : HSEAUDITUPDATE
# =============================================================================
class HSEAuditUpdate(BaseModel):
    """
    Structure permettant la modification partielle d'un formulaire déjà enregistré.
    Tous les attributs sont facultatifs (Optional) pour permettre les patchs ciblés.
    """
    reference: Optional[str] = None
    secteur: Optional[str] = None
    intervenants: Optional[str] = None
    date_audit: Optional[str] = None
    commentaires_generaux: Optional[str] = None

    taux_conformite: Optional[float] = None
    total_conforme: Optional[int] = None
    total_non_conforme: Optional[int] = None
    total_na: Optional[int] = None

    count_soldee: Optional[int] = None
    count_non_engagee: Optional[int] = None
    count_en_cours: Optional[int] = None
    count_en_retard: Optional[int] = None

    items_data: Optional[Dict[str, Any]] = None


# =============================================================================
# 3. SCHÉMA DE SORTIE : HSEAUDITOUT
# =============================================================================
class HSEAuditOut(BaseModel):
    """
    Structure complète d'un audit retourné au frontend pour consultation ou impression.
    Inclut les métadonnées système (id, user_id, created_at).
    """
    id: int
    reference: str
    form_type: str
    secteur: str
    intervenants: str
    date_audit: str
    commentaires_generaux: Optional[str] = None

    taux_conformite: float
    total_conforme: int
    total_non_conforme: int
    total_na: int

    count_soldee: int
    count_non_engagee: int
    count_en_cours: int
    count_en_retard: int

    items_data: Dict[str, Any]
    user_id: int
    author_name: Optional[str] = None
    created_at: datetime

    class Config:
        # Permet le mappage direct depuis un modèle ORM SQLAlchemy
        from_attributes = True


# =============================================================================
# 4. SCHÉMA STATISTIQUE : HSEAUDITSTATS
# =============================================================================
class HSEAuditStats(BaseModel):
    """
    Agrégats statistiques globaux retournés pour le tableau de bord de synthèse.
    """
    total_audits: int                      # Nombre total d'audits réalisés
    avg_conformite: float                  # Taux moyen de conformité globale
    total_actions_soldee: int              # Cumul des actions clôturées
    total_actions_non_engagee: int         # Cumul des actions en attente
    total_actions_en_cours: int            # Cumul des actions en cours
    total_actions_en_retard: int           # Cumul des actions hors délais
