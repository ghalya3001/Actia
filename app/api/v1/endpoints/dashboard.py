"""
===============================================================================
ENDPOINTS API DASHBOARD & WIDGETS (DASHBOARD.PY)
===============================================================================
Ce module fournit les routes nécessaires à l'affichage et à la personnalisation
dynamique du Dashboard :
  - Consultation des KPIs et snapshots calculés
  - Gestion des widgets configurables par l'utilisateur
  - Catalogue des définitions de KPIs
===============================================================================
"""

from typing import List, Any, Optional, Dict
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.dashboard import KPIDefinition, KPISnapshot, DashboardWidget
from app.services.kpi_service import KPIService

router = APIRouter()


# Schemas Pydantic légers pour le Dashboard
class KPIDefinitionOut(BaseModel):
    id: int
    name: str
    label: str
    description: Optional[str] = None
    form_type: str
    source_table: str
    aggregation: str
    chart_type: str
    display_order: int

    class Config:
        from_attributes = True


class KPISnapshotOut(BaseModel):
    id: int
    kpi_id: int
    kpi_name: str
    kpi_label: str
    chart_type: str
    value: Optional[float] = None
    breakdown_data: Optional[Dict[str, Any]] = None
    computed_at: Any


class DashboardWidgetOut(BaseModel):
    id: int
    kpi_id: int
    kpi_name: str
    kpi_label: str
    chart_type: str
    position_x: int
    position_y: int
    width: int
    height: int
    extra_config: Optional[Dict[str, Any]] = None
    value: Optional[float] = None
    breakdown_data: Optional[Dict[str, Any]] = None


class DashboardWidgetCreate(BaseModel):
    kpi_id: int
    position_x: int = 0
    position_y: int = 0
    width: int = 1
    height: int = 1
    extra_config: Optional[Dict[str, Any]] = None


class DashboardWidgetUpdate(BaseModel):
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    extra_config: Optional[Dict[str, Any]] = None


# -----------------------------------------------------------------------------
# 1. CATALOGUE DES DÉFINITIONS DE KPIS
# -----------------------------------------------------------------------------
@router.get(
    "/definitions",
    response_model=List[KPIDefinitionOut],
    summary="Obtenir le catalogue des KPIs disponibles"
)
def get_kpi_definitions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    KPIService.ensure_default_kpi_definitions(db)
    return db.query(KPIDefinition).filter(KPIDefinition.is_active == True).order_by(KPIDefinition.display_order).all()


# -----------------------------------------------------------------------------
# 2. TOUS LES SNAPSHOTS DU RESPONSABLE (Alimentation directe des charts)
# -----------------------------------------------------------------------------
@router.get(
    "/snapshots",
    response_model=List[KPISnapshotOut],
    summary="Obtenir tous les snapshots calculés pour le responsable"
)
def get_user_snapshots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    KPIService.ensure_default_kpi_definitions(db)
    snapshots = db.query(KPISnapshot).filter(KPISnapshot.user_id == current_user.id).all()

    # Si aucun snapshot encore calculé, calculer maintenant
    if not snapshots:
        KPIService.recalculate_kpis_for_user(current_user.id)
        snapshots = db.query(KPISnapshot).filter(KPISnapshot.user_id == current_user.id).all()

    result = []
    for s in snapshots:
        kpi = s.kpi_def
        result.append(KPISnapshotOut(
            id=s.id,
            kpi_id=s.kpi_id,
            kpi_name=kpi.name if kpi else "",
            kpi_label=kpi.label if kpi else "",
            chart_type=kpi.chart_type if kpi else "card",
            value=s.value,
            breakdown_data=s.breakdown_data,
            computed_at=s.computed_at
        ))
    return result


# -----------------------------------------------------------------------------
# 3. WIDGETS CONFIGURÉS PAR L'UTILISATEUR
# -----------------------------------------------------------------------------
@router.get(
    "/widgets",
    response_model=List[DashboardWidgetOut],
    summary="Obtenir la liste des widgets configurés par le responsable"
)
def get_user_widgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    widgets = db.query(DashboardWidget).filter(DashboardWidget.user_id == current_user.id).all()

    # Si l'utilisateur n'a pas encore de widgets, créer la configuration par défaut
    if not widgets:
        KPIService.ensure_default_kpi_definitions(db)
        defs = db.query(KPIDefinition).order_by(KPIDefinition.display_order).limit(6).all()
        for idx, kdef in enumerate(defs):
            w = DashboardWidget(
                user_id=current_user.id,
                kpi_id=kdef.id,
                position_x=idx % 3,
                position_y=idx // 3,
                width=1,
                height=1
            )
            db.add(w)
        db.commit()
        widgets = db.query(DashboardWidget).filter(DashboardWidget.user_id == current_user.id).all()

    # Récupération des valeurs snapshots associées
    res = []
    for w in widgets:
        kdef = w.kpi_def
        snap = db.query(KPISnapshot).filter(
            KPISnapshot.kpi_id == w.kpi_id,
            KPISnapshot.user_id == current_user.id
        ).first()

        res.append(DashboardWidgetOut(
            id=w.id,
            kpi_id=w.kpi_id,
            kpi_name=kdef.name if kdef else "",
            kpi_label=kdef.label if kdef else "",
            chart_type=kdef.chart_type if kdef else "card",
            position_x=w.position_x,
            position_y=w.position_y,
            width=w.width,
            height=w.height,
            extra_config=w.extra_config,
            value=snap.value if snap else 0.0,
            breakdown_data=snap.breakdown_data if snap else None
        ))
    return res


@router.post(
    "/widgets",
    response_model=DashboardWidgetOut,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un widget personnalisé"
)
def add_widget(
    widget_in: DashboardWidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    w = DashboardWidget(
        user_id=current_user.id,
        kpi_id=widget_in.kpi_id,
        position_x=widget_in.position_x,
        position_y=widget_in.position_y,
        width=widget_in.width,
        height=widget_in.height,
        extra_config=widget_in.extra_config
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return DashboardWidgetOut(
        id=w.id,
        kpi_id=w.kpi_id,
        kpi_name=w.kpi_def.name,
        kpi_label=w.kpi_def.label,
        chart_type=w.kpi_def.chart_type,
        position_x=w.position_x,
        position_y=w.position_y,
        width=w.width,
        height=w.height,
        extra_config=w.extra_config
    )


@router.put(
    "/widgets/{widget_id}",
    summary="Mettre à jour la disposition d'un widget"
)
def update_widget(
    widget_id: int,
    widget_in: DashboardWidgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    w = db.query(DashboardWidget).filter(
        DashboardWidget.id == widget_id,
        DashboardWidget.user_id == current_user.id
    ).first()
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget introuvable.")

    for k, v in widget_in.model_dump(exclude_unset=True).items():
        setattr(w, k, v)
    db.commit()
    return {"message": "Widget mis à jour avec succès"}


@router.delete(
    "/widgets/{widget_id}",
    summary="Supprimer un widget de son dashboard"
)
def delete_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    w = db.query(DashboardWidget).filter(
        DashboardWidget.id == widget_id,
        DashboardWidget.user_id == current_user.id
    ).first()
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget introuvable.")
    db.delete(w)
    db.commit()
    return {"message": "Widget supprimé."}
