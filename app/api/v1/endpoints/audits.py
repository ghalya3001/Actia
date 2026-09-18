"""
===============================================================================
ENDPOINTS API AUDITS & FORMULAIRES DE SÉCURITÉ HSE (AUDITS.PY)
===============================================================================
Rôle :
  Expose l'ensemble des opérations CRUD pour les formulaires de contrôle terrain :
  - `POST /`            : Création d'un audit, tournée ou permis avec ventilation relationnelle.
  - `GET  /`            : Liste filtrable des soumissions du manager connecté (dates, secteurs, types).
  - `GET  /stats`       : Statistiques consolidées et instantanées pour le Dashboard.
  - `GET  /{audit_id}`  : Consultation détaillée unitaire avec reconstitution de `items_data`.
  - `PUT  /{audit_id}`  : Modification partielle ou mise à jour des statuts de plans d'action.
  - `DELETE /{audit_id}`: Suppression définitive en cascade BDD.

Caractéristiques architecturales :
  - Toutes les routes sont protégées par le token JWT (`Depends(get_current_user)`).
  - Recalcul non-bloquant en arrière-plan : Après chaque création, modification ou suppression,
    une tâche de fond FastAPI (`BackgroundTasks`) recalcule les indicateurs KPIs sans ralentir
    la réponse retournée au client.
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


# =============================================================================
# 1. CRÉATION D'UN NOUVEL ENREGISTREMENT HSE
# =============================================================================
@router.post(
    "/",
    response_model=HSEAuditOut,
    status_code=status.HTTP_201_CREATED,
    summary="Créer et enregistrer un nouveau formulaire HSE"
)
def create_audit(
    audit_in: HSEAuditCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [CREATE] Enregistre une nouvelle fiche HSE.
    Ventile les données dans la table mère 'form_submissions' et ses tables filles spécialisées,
    puis déclenche le recalcul des indicateurs KPIs en tâche de fond asynchrone.

    Args:
        audit_in (HSEAuditCreate): Corps JSON validé de la soumission.
        background_tasks (BackgroundTasks): Gestionnaire de tâches asynchrones FastAPI.
        db (Session): Session BDD active.
        current_user (User): Manager connecté auteur de la saisie.

    Returns:
        HSEAuditOut: Fiche enregistrée avec son identifiant généré.
    """
    # Sauvegarde relationnelle et obtention de la structure reconstituée
    submission_data = SubmissionService.create_submission(
        db=db,
        audit_in=audit_in,
        user_id=current_user.id
    )

    # Déclenchement non-bloquant du recalcul des KPIs impactés pour ce manager
    background_tasks.add_task(
        KPIService.recalculate_kpis_for_user,
        user_id=current_user.id
    )

    return submission_data


# =============================================================================
# 2. LECTURE ET FILTRAGE DES FORMULAIRES DU MANAGER
# =============================================================================
@router.get(
    "/",
    response_model=List[HSEAuditOut],
    summary="Récupérer et filtrer la liste des fiches du responsable connecté"
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
    [READ ALL & FILTER] Retourne l'historique complet des fiches réalisées par le manager.
    Supporte les filtres combinables :
      - `date_audit` : Date exacte (YYYY-MM-DD).
      - `date_from` / `date_to` : Intervalle chronologique.
      - `form_type` : Catégorie ('audit_hse', 'tournee_hse', 'permis_travail', etc.).
      - `secteur` : Recherche textuelle dans le secteur ou les intervenants.
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


# =============================================================================
# 3. STATISTIQUES CONSOLIDÉES POUR LE TABLEAU DE BORD
# =============================================================================
@router.get(
    "/stats",
    response_model=HSEAuditStats,
    summary="Obtenir les indicateurs statistiques consolidés"
)
def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [READ STATS] Fournit un résumé chiffré instantané (total audits, taux moyen de conformité,
    répartition des actions : soldées, non engagées, en cours, en retard).
    Lit en priorité la table de cache `kpi_snapshots`.
    """
    return KPIService.get_user_stats(db=db, user_id=current_user.id)


# =============================================================================
# 4. CONSULTATION DÉTAILLÉE D'UNE FICHE PAR SON IDENTIFIANT
# =============================================================================
@router.get(
    "/{audit_id}",
    response_model=HSEAuditOut,
    summary="Consulter le détail complet d'un formulaire par son ID"
)
def get_audit_by_id(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [READ ONE] Récupère une fiche avec son arborescence de questions, constats et photos.
    Vérifie que la fiche appartient bien au manager connecté.
    """
    return SubmissionService.get_submission_by_id(
        db=db,
        audit_id=audit_id,
        user_id=current_user.id
    )


# =============================================================================
# 5. MODIFICATION D'UNE FICHE EXISTANTE
# =============================================================================
@router.put(
    "/{audit_id}",
    response_model=HSEAuditOut,
    summary="Mettre à jour les données ou actions d'un audit existant"
)
def update_audit(
    audit_id: int,
    audit_in: HSEAuditUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [UPDATE] Met à jour les métadonnées ou le statut des actions correctives.
    Déclenche en tâche de fond le recalcul des KPIs pour actualiser les graphiques.
    """
    updated_data = SubmissionService.update_submission(
        db=db,
        audit_id=audit_id,
        audit_in=audit_in,
        user_id=current_user.id
    )

    # Recalcul asynchrone des indicateurs du dashboard
    background_tasks.add_task(
        KPIService.recalculate_kpis_for_user,
        user_id=current_user.id
    )

    return updated_data


# =============================================================================
# 6. SUPPRESSION D'UNE FICHE
# =============================================================================
@router.delete(
    "/{audit_id}",
    status_code=status.HTTP_200_OK,
    summary="Supprimer définitivement un formulaire par son ID"
)
def delete_audit(
    audit_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [DELETE] Supprime définitivement la fiche et ses lignes d'évaluation en cascade.
    Met à jour les indicateurs du dashboard après suppression.
    """
    SubmissionService.delete_submission(
        db=db,
        audit_id=audit_id,
        user_id=current_user.id
    )

    # Recalcul en arrière-plan pour déduire la fiche supprimée des statistiques
    background_tasks.add_task(
        KPIService.recalculate_kpis_for_user,
        user_id=current_user.id
    )

    return {"message": f"La fiche ID {audit_id} a été supprimée avec succès."}
