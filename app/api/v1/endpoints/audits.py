"""
===============================================================================
ENDPOINTS API AUDITS & TOURNÉES HSE (AUDITS.PY)
===============================================================================
Ce module définit l'ensemble des routes CRUD (Create, Read, Update, Delete)
pour la gestion des Fiches d'Audit HSE (FGSI-001) et des Tournées HSE (FGSI-010-Ind:A).

Fonctionnalités gérées :
  - Création d'audit avec calcul automatique des scores de conformité
  - Recherche et filtrage dynamique (par date, type de formulaire, secteur)
  - Consultation par ID
  - Modification et mise à jour d'un audit existant
  - Suppression définitive
  - Agrégation de statistiques KPIs pour le Dashboard HSE

Auteurs / Équipe : CIPI ACTIA - Plateforme HSE
===============================================================================
"""

from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.audit import HSEAudit
from app.schemas.audit import HSEAuditCreate, HSEAuditUpdate, HSEAuditOut, HSEAuditStats

router = APIRouter()

# -----------------------------------------------------------------------------
# 1. CRÉATION D'UN NOUVEL AUDIT / TOURNÉE HSE
# -----------------------------------------------------------------------------
@router.post("/", response_model=HSEAuditOut, status_code=status.HTTP_201_CREATED, summary="Créer et enregistrer un audit HSE")
def create_audit(
    audit_in: HSEAuditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [CREATE] Enregistre une nouvelle fiche d'audit HSE (FGSI-001) soumise par le responsable connecté.
    """
    db_audit = HSEAudit(
        reference=audit_in.reference,
        form_type=audit_in.form_type,
        secteur=audit_in.secteur,
        intervenants=audit_in.intervenants,
        date_audit=audit_in.date_audit,
        commentaires_generaux=audit_in.commentaires_generaux,
        taux_conformite=audit_in.taux_conformite,
        total_conforme=audit_in.total_conforme,
        total_non_conforme=audit_in.total_non_conforme,
        total_na=audit_in.total_na,
        count_soldee=audit_in.count_soldee,
        count_non_engagee=audit_in.count_non_engagee,
        count_en_cours=audit_in.count_en_cours,
        count_en_retard=audit_in.count_en_retard,
        items_data=audit_in.items_data,
        user_id=current_user.id,
    )
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit


# 2. READ ALL AUDITS WITH FILTERS
@router.get("/", response_model=List[HSEAuditOut], summary="Récupérer et filtrer la liste des audits du responsable")
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
    [READ ALL & FILTER] Retourne les audits réalisés par le responsable connecté avec filtre optionnel par date_audit, form_type, et secteur.
    """
    query = db.query(HSEAudit).filter(HSEAudit.user_id == current_user.id)
    
    if date_audit:
        query = query.filter(HSEAudit.date_audit == date_audit)
    if date_from:
        query = query.filter(HSEAudit.date_audit >= date_from)
    if date_to:
        query = query.filter(HSEAudit.date_audit <= date_to)
    if form_type:
        if form_type == "audit_hse":
            query = query.filter(HSEAudit.form_type.in_(["audit_hse", "audit_hse_complet"]))
        else:
            query = query.filter(HSEAudit.form_type == form_type)
    if secteur:
        query = query.filter(HSEAudit.secteur.ilike(f"%{secteur}%"))
        
    audits = query.order_by(HSEAudit.created_at.desc()).all()
    return audits


# 3. READ AUDIT STATS (FOR DASHBOARD)
@router.get("/stats", response_model=HSEAuditStats, summary="Obtenir les statistiques globales des audits")
def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [READ STATS] Agrège les KPIs d'audits pour alimenter le Dashboard HSE dynamique.
    """
    user_audits = db.query(HSEAudit).filter(HSEAudit.user_id == current_user.id).all()
    
    total_audits = len(user_audits)
    if total_audits == 0:
        return HSEAuditStats(
            total_audits=0,
            avg_conformite=0.0,
            total_actions_soldee=0,
            total_actions_non_engagee=0,
            total_actions_en_cours=0,
            total_actions_en_retard=0,
        )

    avg_conf = sum(a.taux_conformite for a in user_audits) / total_audits
    soldee = sum(a.count_soldee for a in user_audits)
    non_engagee = sum(a.count_non_engagee for a in user_audits)
    en_cours = sum(a.count_en_cours for a in user_audits)
    en_retard = sum(a.count_en_retard for a in user_audits)

    return HSEAuditStats(
        total_audits=total_audits,
        avg_conformite=round(avg_conf, 1),
        total_actions_soldee=soldee,
        total_actions_non_engagee=non_engagee,
        total_actions_en_cours=en_cours,
        total_actions_en_retard=en_retard,
    )


# 4. READ ONE AUDIT BY ID
@router.get("/{audit_id}", response_model=HSEAuditOut, summary="Récupérer un audit par son ID")
def get_audit_by_id(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [READ ONE] Récupère le détail d'un audit spécifique par son identifiant.
    """
    audit = db.query(HSEAudit).filter(HSEAudit.id == audit_id, HSEAudit.user_id == current_user.id).first()
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit introuvable avec l'ID {audit_id}."
        )
    return audit


# 5. UPDATE AUDIT BY ID
@router.put("/{audit_id}", response_model=HSEAuditOut, summary="Mettre à jour un audit existant")
def update_audit(
    audit_id: int,
    audit_in: HSEAuditUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [UPDATE] Met à jour les informations ou les constats/actions d'un audit existant.
    """
    audit = db.query(HSEAudit).filter(HSEAudit.id == audit_id, HSEAudit.user_id == current_user.id).first()
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit introuvable avec l'ID {audit_id}."
        )
    
    update_data = audit_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(audit, field, value)

    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


# 6. DELETE AUDIT BY ID
@router.delete("/{audit_id}", status_code=status.HTTP_200_OK, summary="Supprimer un audit par son ID")
def delete_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    [DELETE] Supprime définitivement une fiche d'audit de la base de données.
    """
    audit = db.query(HSEAudit).filter(HSEAudit.id == audit_id, HSEAudit.user_id == current_user.id).first()
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit introuvable avec l'ID {audit_id}."
        )
    
    db.delete(audit)
    db.commit()
    return {"message": f"L'audit ID {audit_id} a été supprimé avec succès."}
