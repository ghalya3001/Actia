"""
===============================================================================
ENDPOINTS API DU TABLEAU DE BORD ET DES WIDGETS (DASHBOARD.PY)
===============================================================================
Rôle :
  Fournit l'API pour alimenter et personnaliser dynamiquement le Dashboard HSE :
  1. `GET  /definitions` : Catalogue des indicateurs configurables disponibles.
  2. `GET  /snapshots`   : Liste des calculs en cache pour alimenter instantanément Chart.js.
  3. `GET  /widgets`     : Grille de widgets personnalisée du manager (avec fallback par défaut).
  4. `POST /widgets`     : Ajout d'un nouveau widget sur le tableau de bord.
  5. `PUT  /widgets/{id}`: Mise à jour des coordonnées (X, Y) et dimensions (Largeur, Hauteur).
  6. `DELETE /widgets/{id}`: Retrait d'un widget de la vue.

Équipe de maintenance :
  - Si un manager n'a encore configuré aucun widget lors de sa première visite sur `/widgets`,
    le backend initialise automatiquement les 6 premiers widgets du catalogue en grille 3x2.
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


# =============================================================================
# 1. SCHÉMAS PYDANTIC DÉDIÉS AUX ENDPOINTS DU DASHBOARD
# =============================================================================
class KPIDefinitionOut(BaseModel):
    """
    Format d'exposition d'une définition du catalogue d'indicateurs.
    """
    id: int
    name: str                          # Identifiant technique (ex: 'avg_conformite')
    label: str                         # Titre affiché (ex: 'Taux Moyen de Conformité')
    description: Optional[str] = None  # Explication pédagogique
    form_type: str                     # Périmètre ('all', 'audit_hse', etc.)
    source_table: str                  # Table source SQL
    aggregation: str                   # Fonction d'agrégation ('AVG', 'COUNT', etc.)
    chart_type: str                    # Type de visuel ('card', 'doughnut', 'bar', 'line')
    display_order: int                 # Ordre d'affichage

    class Config:
        from_attributes = True


class KPISnapshotOut(BaseModel):
    """
    Données consolidées d'un snapshot en cache envoyées au frontend pour tracer les graphiques.
    """
    id: int
    kpi_id: int
    kpi_name: str
    kpi_label: str
    chart_type: str
    value: Optional[float] = None
    breakdown_data: Optional[Dict[str, Any]] = None  # Séries de données groupées pour Chart.js
    computed_at: Any


class DashboardWidgetOut(BaseModel):
    """
    Configuration complète d'un widget de tableau de bord prêt à l'affichage.
    """
    id: int
    kpi_id: int
    kpi_name: str
    kpi_label: str
    chart_type: str
    position_x: int                    # Colonne d'ancrage sur la grille (0, 1, 2...)
    position_y: int                    # Ligne d'ancrage sur la grille (0, 1, 2...)
    width: int                         # Largeur en nombre de colonnes
    height: int                        # Hauteur en nombre de lignes
    extra_config: Optional[Dict[str, Any]] = None
    value: Optional[float] = None
    breakdown_data: Optional[Dict[str, Any]] = None


class DashboardWidgetCreate(BaseModel):
    """
    Données nécessaires pour épingler un nouvel indicateur sur le tableau de bord.
    """
    kpi_id: int
    position_x: int = 0
    position_y: int = 0
    width: int = 1
    height: int = 1
    extra_config: Optional[Dict[str, Any]] = None


class DashboardWidgetUpdate(BaseModel):
    """
    Données de redimensionnement ou repositionnement d'un widget (Drag & Drop / Resize).
    """
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    extra_config: Optional[Dict[str, Any]] = None


# =============================================================================
# 2. ENDPOINT : CATALOGUE DES DÉFINITIONS DE KPIS
# =============================================================================
@router.get(
    "/definitions",
    response_model=List[KPIDefinitionOut],
    summary="Obtenir le catalogue de tous les indicateurs configurables disponibles"
)
def get_kpi_definitions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retourne l'ensemble des définitions de KPIs actives, triées selon leur ordre d'affichage.
    Initialise les indicateurs par défaut si la base est neuve.
    """
    KPIService.ensure_default_kpi_definitions(db)
    return db.query(KPIDefinition).filter(KPIDefinition.is_active == True).order_by(KPIDefinition.display_order).all()


# =============================================================================
# 3. ENDPOINT : SNAPSHOTS PRÉ-CALCULÉS DU MANAGER (ALIMENTATION DES CHARTS)
# =============================================================================
@router.get(
    "/snapshots",
    response_model=List[KPISnapshotOut],
    summary="Obtenir tous les snapshots en cache calculés pour le responsable connecté"
)
def get_user_snapshots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Récupère instantanément depuis 'kpi_snapshots' l'ensemble des valeurs numériques
    et séries groupées (camembert, barres, séries temporelles) calculées pour ce manager.
    Si aucun snapshot n'est présent, un calcul initial est immédiatement exécuté.
    """
    KPIService.ensure_default_kpi_definitions(db)
    snapshots = db.query(KPISnapshot).filter(KPISnapshot.user_id == current_user.id).all()

    # Si la table de cache est vide pour cet utilisateur, déclencher un premier calcul
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


# =============================================================================
# 4. ENDPOINT : CONSULTATION DES WIDGETS DU TABLEAU DE BORD
# =============================================================================
@router.get(
    "/widgets",
    response_model=List[DashboardWidgetOut],
    summary="Obtenir la grille des widgets personnalisés du responsable connecté"
)
def get_user_widgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retourne la disposition actuelle des widgets du tableau de bord.
    Si l'utilisateur arrive pour la première fois, génère automatiquement
    une disposition initiale standard composée de 6 widgets représentatifs.
    """
    widgets = db.query(DashboardWidget).filter(DashboardWidget.user_id == current_user.id).all()

    # Génération automatique de la grille par défaut si aucune configuration n'existe
    if not widgets:
        KPIService.ensure_default_kpi_definitions(db)
        defs = db.query(KPIDefinition).order_by(KPIDefinition.display_order).limit(6).all()
        for idx, kdef in enumerate(defs):
            w = DashboardWidget(
                user_id=current_user.id,
                kpi_id=kdef.id,
                position_x=idx % 3,   # Répartition sur 3 colonnes
                position_y=idx // 3,  # Calcul de la rangée
                width=1,
                height=1
            )
            db.add(w)
        db.commit()
        widgets = db.query(DashboardWidget).filter(DashboardWidget.user_id == current_user.id).all()

    # Jointure avec les valeurs actuelles des snapshots pour chaque widget
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


# =============================================================================
# 5. ENDPOINT : AJOUT D'UN NOUVEAU WIDGET
# =============================================================================
@router.post(
    "/widgets",
    response_model=DashboardWidgetOut,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un widget personnalisé sur le tableau de bord"
)
def add_widget(
    widget_in: DashboardWidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Enregistre un nouveau widget positionné sur la grille du manager.
    """
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


# =============================================================================
# 6. ENDPOINT : MODIFICATION D'UN WIDGET (REPOSITIONNEMENT)
# =============================================================================
@router.put(
    "/widgets/{widget_id}",
    summary="Mettre à jour la position ou la dimension d'un widget"
)
def update_widget(
    widget_id: int,
    widget_in: DashboardWidgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Met à jour les coordonnées X, Y ou les dimensions Width, Height du widget spécifié.
    """
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


# =============================================================================
# 7. ENDPOINT : SUPPRESSION D'UN WIDGET
# =============================================================================
@router.delete(
    "/widgets/{widget_id}",
    summary="Supprimer un widget du tableau de bord"
)
def delete_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retire le widget de la vue du manager sans supprimer la définition du KPI associée.
    """
    w = db.query(DashboardWidget).filter(
        DashboardWidget.id == widget_id,
        DashboardWidget.user_id == current_user.id
    ).first()
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget introuvable.")
    db.delete(w)
    db.commit()
    return {"message": "Widget supprimé."}
