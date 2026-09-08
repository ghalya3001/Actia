"""
===============================================================================
ENDPOINTS API AUDITS & TOURNÉES HSE (AUDITS.PY)
===============================================================================
Ce module définit l'ensemble des routes CRUD (Create, Read, Update, Delete)
pour la gestion des Fiches d'Audit HSE (FGSI-001), Tournées HSE (FGSI-010)
et Permis de Travail (FGSI-PERMIS).

Caractéristiques architecturales :
  - Compatible à 100% avec les formulaires frontend (contrats préservés)
  - Données stockées dans les tables normalisées (form_submissions, audit_hse_submissions, items)
  - Recalcul automatique des KPIs en arrière-plan (FastAPI BackgroundTasks)
  - Affichage instantané des statistiques et KPIs

Auteurs / Équipe : CIPI ACTIA - Plateforme HSE
===============================================================================
"""

from typing import List, Any, Optional
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.audit import HSEAuditCreate, HSEAuditUpdate, HSEAuditOut, HSEAuditStats
from app.services.submission_service import SubmissionService
from app.services.kpi_service import KPIService

router = APIRouter()


# -----------------------------------------------------------------------------
# 1. CRÉATION D'UN NOUVEL AUDIT / TOURNÉE / PERMIS HSE
# -----------------------------------------------------------------------------
@router.post(
    "/",
    response_model=HSEAuditOut,
    status_code=status.HTTP_201_CREATED,
    summary="Créer et enregistrer un formulaire HSE"
)
def create_audit(
    audit_in: HSEAuditCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [CREATE] Enregistre une nouvelle fiche HSE.
    Ventile les données dans form_submissions et ses tables enfants,
    puis déclenche le recalcul des KPIs en arrière-plan.
    """
    submission_data = SubmissionService.create_submission(
        db=db,
        audit_in=audit_in,
        user_id=current_user.id
    )

    # 🚀 Déclenchement non-bloquant du recalcul des KPIs impactés
    background_tasks.add_task(
        KPIService.recalculate_kpis_for_user,
        user_id=current_user.id
    )

    return submission_data


# -----------------------------------------------------------------------------
# 2. LECTURE & FILTRAGE DES SOUMISSIONS DU RESPONSABLE
# -----------------------------------------------------------------------------
@router.get(
    "/",
    response_model=List[HSEAuditOut],
    summary="Récupérer et filtrer la liste des audits du responsable"
)
def get_user_audits(
    date_audit: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    form_type: Optional[str] = None,
    secteur: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [READ ALL & FILTER] Retourne les fiches réalisées par le responsable connecté
    avec filtres dynamiques (date, form_type, secteur/intervenants).
    """
    return SubmissionService.get_all_submissions(
        db=db,
        user_id=current_user.id,
        date_audit=date_audit,
        date_from=date_from,
        date_to=date_to,
        form_type=form_type,
        secteur=secteur
    )


# -----------------------------------------------------------------------------
# 3. STATISTIQUES GLOBALES POUR LE DASHBOARD
# -----------------------------------------------------------------------------
@router.get(
    "/stats",
    response_model=HSEAuditStats,
    summary="Obtenir les statistiques globales des audits"
)
def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [READ STATS] Retourne instantanément les KPIs pré-calculés depuis kpi_snapshots.
    """
    return KPIService.get_user_stats(db=db, user_id=current_user.id)


# -----------------------------------------------------------------------------
# 4. CONSULTATION D'UNE FICHE PAR SON IDENTIFIANT
# -----------------------------------------------------------------------------
@router.get(
    "/{audit_id}",
    response_model=HSEAuditOut,
    summary="Récupérer un audit par son ID"
)
def get_audit_by_id(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [READ ONE] Récupère le détail complet d'une fiche avec reconstitution
    automatique du dictionnaire items_data.
    """
    return SubmissionService.get_submission_by_id(
        db=db,
        audit_id=audit_id,
        user_id=current_user.id
    )


# -----------------------------------------------------------------------------
# 5. MODIFICATION D'UNE FICHE EXISTANTE
# -----------------------------------------------------------------------------
@router.put(
    "/{audit_id}",
    response_model=HSEAuditOut,
    summary="Mettre à jour un audit existant"
)
def update_audit(
    audit_id: int,
    audit_in: HSEAuditUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [UPDATE] Met à jour les informations ou les constats/actions d'une fiche.
    Déclenche le recalcul des KPIs pour refléter les nouveaux statuts d'action.
    """
    updated_data = SubmissionService.update_submission(
        db=db,
        audit_id=audit_id,
        audit_in=audit_in,
        user_id=current_user.id
    )

    # 🚀 Recalcul en arrière-plan
    background_tasks.add_task(
        KPIService.recalculate_kpis_for_user,
        user_id=current_user.id
    )

    return updated_data


# -----------------------------------------------------------------------------
# 6. SUPPRESSION D'UNE FICHE
# -----------------------------------------------------------------------------
@router.delete(
    "/{audit_id}",
    status_code=status.HTTP_200_OK,
    summary="Supprimer un audit par son ID"
)
def delete_audit(
    audit_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [DELETE] Supprime définitivement une fiche et ses items en cascade.
    Déclenche le recalcul des KPIs après suppression.
    """
    SubmissionService.delete_submission(
        db=db,
        audit_id=audit_id,
        user_id=current_user.id
    )

    # 🚀 Recalcul en arrière-plan
    background_tasks.add_task(
        KPIService.recalculate_kpis_for_user,
        user_id=current_user.id
    )

    return {"message": f"La fiche ID {audit_id} a été supprimée avec succès."}
