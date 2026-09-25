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
from datetime import datetime, date
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import or_, func, extract, and_
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_approved_user
from app.models.user import User
from app.models.dashboard import KPIDefinition, KPISnapshot, DashboardWidget
from app.models.submission import (
    FormSubmission,
    AuditHSESubmission,
    TourneeHSESubmission,
    PermisTravailSubmission,
    AccidentTravailSubmission,
    AccidentTravailMonthlyItem,
    AuditHSEItem,
    TourneeHSEItem,
)
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
    current_user: User = Depends(get_current_approved_user)
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
    current_user: User = Depends(get_current_approved_user)
) -> Any:
    """
    Récupère instantanément depuis 'kpi_snapshots' l'ensemble des valeurs numériques
    et séries groupées (camembert, barres, séries temporelles) calculées pour ce manager.
    Si aucun snapshot n'est présent, un calcul initial est immédiatement exécuté.
    """
    KPIService.ensure_default_kpi_definitions(db)
    snapshots = db.query(KPISnapshot).filter(
        or_(KPISnapshot.user_id == current_user.id, KPISnapshot.user_id.is_(None))
    ).all()

    # Si la table de cache est vide pour cet utilisateur, déclencher un premier calcul centralisé
    if not snapshots:
        KPIService.recalculate_kpis_for_user()
        snapshots = db.query(KPISnapshot).filter(
            or_(KPISnapshot.user_id == current_user.id, KPISnapshot.user_id.is_(None))
        ).all()

    # Déduplication par kpi_id en privilégiant le snapshot spécifique utilisateur s'il existe
    unique_snapshots = {}
    for s in snapshots:
        if s.kpi_id not in unique_snapshots or s.user_id is not None:
            unique_snapshots[s.kpi_id] = s

    result = []
    for s in unique_snapshots.values():
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
    current_user: User = Depends(get_current_approved_user)
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
            or_(KPISnapshot.user_id == current_user.id, KPISnapshot.user_id.is_(None))
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
    current_user: User = Depends(get_current_approved_user)
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
    current_user: User = Depends(get_current_approved_user)
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
    current_user: User = Depends(get_current_approved_user)
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


# =============================================================================
# 8. ENDPOINT : STATISTIQUES CONSOLIDÉES DU DASHBOARD (DONNÉES RÉELLES BDD)
# =============================================================================

# Noms de mois en français pour les labels des graphiques
MOIS_FR = [
    "", "Janv", "Fév", "Mar", "Avr", "Mai", "Juin",
    "Juil", "Août", "Sept", "Oct", "Nov", "Déc"
]

# Noms des 7 sections thématiques d'audit/tournée HSE
SECTION_LABELS = {
    1: "EPI & Tenue",
    2: "ATEX / Élec",
    3: "Incendie & Évac",
    4: "Ergonomie",
    5: "5S & Ordre",
    6: "Produits Chimiques",
    7: "Risques Machine",
}


class DashboardStatsOut(BaseModel):
    """
    Structure complète des données consolidées du dashboard HSE.
    Alimentée depuis les tables réelles de la base de données.
    """
    # --- Filtres appliqués ---
    filter_year: Optional[int] = None
    filter_date_debut: Optional[str] = None
    filter_date_fin: Optional[str] = None
    available_years: List[int] = []

    # --- Scorecards ---
    total_audits: int = 0
    avg_conformite: float = 0.0
    actions_en_retard: int = 0
    jours_sans_accident: int = 0
    dernier_accident_date: Optional[str] = None

    # TF du mois courant et variation
    tf_courant: float = 0.0
    tf_variation: float = 0.0
    conformite_derniere_tournee: float = 0.0
    conformite_variation: float = 0.0

    # --- Graphique : Courbe mensuelle TF & IF ---
    monthly_labels: List[str] = []
    monthly_tf: List[float] = []
    monthly_if: List[float] = []
    target_tf: float = 2.5

    # --- Graphique : Évolution conformité ---
    conformite_labels: List[str] = []
    conformite_values: List[float] = []

    # --- Graphique : Radar thématique ---
    radar_labels: List[str] = []
    radar_scores: List[float] = []

    # --- Graphique : Donut actions correctives ---
    actions_soldee: int = 0
    actions_en_cours: int = 0
    actions_non_engagee: int = 0
    actions_retard_count: int = 0

    # --- Conformité par secteur ---
    secteur_labels: List[str] = []
    secteur_values: List[float] = []

    # --- Tableau : Actions en retard détaillées ---
    actions_retard_details: List[Dict[str, Any]] = []

    # --- Permis de travail ---
    total_permis: int = 0


def _parse_date_audit(date_str: str) -> Optional[date]:
    """Parse une date d'audit au format ISO (YYYY-MM-DD) ou DD/MM/YYYY."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


@router.get(
    "/stats",
    response_model=DashboardStatsOut,
    summary="Obtenir les statistiques consolidées du dashboard avec filtres de date"
)
def get_dashboard_stats(
    year: Optional[int] = Query(None, description="Filtrer par année (ex: 2026)"),
    date_debut: Optional[str] = Query(None, description="Date de début au format YYYY-MM-DD"),
    date_fin: Optional[str] = Query(None, description="Date de fin au format YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user)
) -> Any:
    """
    Retourne l'ensemble des données consolidées du Dashboard HSE calculées
    directement depuis les tables de la base de données.
    Supporte 3 modes de filtrage combinables :
      - Par année uniquement (year=2026)
      - Par plage de dates (date_debut=2026-01-01&date_fin=2026-06-30)
      - Par année + plage de dates
    """
    result = DashboardStatsOut(
        filter_year=year,
        filter_date_debut=date_debut,
        filter_date_fin=date_fin,
    )

    # ------------------------------------------------------------------
    # 0. Déterminer les années disponibles dans la base
    # ------------------------------------------------------------------
    all_submissions = db.query(FormSubmission).all()
    all_accidents = db.query(AccidentTravailSubmission).all()
    years_set = set()
    for s in all_submissions:
        d = _parse_date_audit(s.date_audit)
        if d:
            years_set.add(d.year)
    for a in all_accidents:
        if a.annee:
            years_set.add(a.annee)
    if not years_set:
        years_set.add(datetime.now().year)
    result.available_years = sorted(years_set, reverse=True)

    # ------------------------------------------------------------------
    # 1. Filtrer les soumissions selon les critères de date
    # ------------------------------------------------------------------
    has_date_filter = bool(year or date_debut or date_fin)
    filtered_submissions = []
    for s in all_submissions:
        d = _parse_date_audit(s.date_audit)
        if not d:
            if not has_date_filter:
                filtered_submissions.append(s)
            continue
        if year and d.year != year:
            continue
        if date_debut:
            try:
                dd = datetime.strptime(date_debut, "%Y-%m-%d").date()
                if d < dd:
                    continue
            except ValueError:
                pass
        if date_fin:
            try:
                df = datetime.strptime(date_fin, "%Y-%m-%d").date()
                if d > df:
                    continue
            except ValueError:
                pass
        filtered_submissions.append(s)

    submission_ids = {s.id for s in filtered_submissions}

    # ------------------------------------------------------------------
    # 2. Scorecards : Total audits & Conformité moyenne
    # ------------------------------------------------------------------
    result.total_audits = len(filtered_submissions)
    if result.total_audits > 0:
        result.avg_conformite = round(
            sum(s.taux_conformite for s in filtered_submissions) / result.total_audits, 1
        )

    # ------------------------------------------------------------------
    # 3. Agrégation des actions correctives (audits + tournées filtrés)
    # ------------------------------------------------------------------
    audits = [s for s in filtered_submissions if s.form_type == "audit_hse"]
    tournees = [s for s in filtered_submissions if s.form_type == "tournee_hse"]

    # Récupérer les détails via les tables filles
    audit_details = db.query(AuditHSESubmission).filter(
        AuditHSESubmission.id.in_(submission_ids)
    ).all() if submission_ids else []
    tournee_details = db.query(TourneeHSESubmission).filter(
        TourneeHSESubmission.id.in_(submission_ids)
    ).all() if submission_ids else []

    soldee = sum(a.count_soldee for a in audit_details) + sum(t.count_soldee for t in tournee_details)
    non_engagee = sum(a.count_non_engagee for a in audit_details) + sum(t.count_non_engagee for t in tournee_details)
    en_cours = sum(a.count_en_cours for a in audit_details) + sum(t.count_en_cours for t in tournee_details)
    en_retard = sum(a.count_en_retard for a in audit_details) + sum(t.count_en_retard for t in tournee_details)

    result.actions_soldee = soldee
    result.actions_non_engagee = non_engagee
    result.actions_en_cours = en_cours
    result.actions_retard_count = en_retard
    result.actions_en_retard = en_retard

    # ------------------------------------------------------------------
    # 4. Permis de travail (filtrés)
    # ------------------------------------------------------------------
    permis = db.query(PermisTravailSubmission).filter(
        PermisTravailSubmission.id.in_(submission_ids)
    ).all() if submission_ids else []
    result.total_permis = sum(
        p.nb_plan_prevention + p.nb_permis_hauteur + p.nb_permis_feu for p in permis
    )

    # ------------------------------------------------------------------
    # 5. Courbe mensuelle TF & IF (depuis AccidentTravailMonthlyItem)
    # ------------------------------------------------------------------
    target_year = year or (datetime.now().year)
    accident_subs = db.query(AccidentTravailSubmission).filter(
        AccidentTravailSubmission.annee == target_year
    ).all()

    monthly_tf_map: Dict[int, float] = {}
    monthly_if_map: Dict[int, float] = {}

    for acc_sub in accident_subs:
        for item in acc_sub.monthly_items:
            m = item.mois_index
            if m < 1 or m > 12:
                continue
            # Garder le dernier TF/IF disponible par mois
            monthly_tf_map[m] = item.tf_valeur
            monthly_if_map[m] = item.if_valeur

    # Construire les labels et valeurs pour les mois qui ont des données
    if monthly_tf_map:
        max_month = max(monthly_tf_map.keys())
        for m in range(1, max_month + 1):
            result.monthly_labels.append(MOIS_FR[m])
            result.monthly_tf.append(round(monthly_tf_map.get(m, 0.0), 2))
            result.monthly_if.append(round(monthly_if_map.get(m, 0.0), 2))

        # TF courant = dernier mois avec données
        result.tf_courant = result.monthly_tf[-1] if result.monthly_tf else 0.0
        if len(result.monthly_tf) >= 2:
            result.tf_variation = round(result.monthly_tf[-1] - result.monthly_tf[-2], 2)

    # Target TF depuis la soumission accident
    if accident_subs:
        result.target_tf = accident_subs[0].target_tf or 2.5

    # ------------------------------------------------------------------
    # 6. Jours sans accident (calculé depuis les données mensuelles)
    # ------------------------------------------------------------------
    today = date.today()
    all_accident_subs = db.query(AccidentTravailSubmission).all()
    last_accident_date = None

    for acc_sub in all_accident_subs:
        for item in sorted(acc_sub.monthly_items, key=lambda x: x.mois_index, reverse=True):
            if item.nb_accidents_avec_arret > 0:
                # Approximer la date au milieu du mois
                try:
                    d = date(acc_sub.annee, item.mois_index, 15)
                    if last_accident_date is None or d > last_accident_date:
                        last_accident_date = d
                except ValueError:
                    pass

    if last_accident_date:
        result.jours_sans_accident = (today - last_accident_date).days
        result.dernier_accident_date = last_accident_date.strftime("%d/%m/%Y")
    else:
        # Si aucun accident enregistré, compter depuis la plus ancienne soumission
        if all_submissions:
            dates_parsed = [_parse_date_audit(s.date_audit) for s in all_submissions]
            valid_dates = [d for d in dates_parsed if d]
            if valid_dates:
                oldest = min(valid_dates)
                result.jours_sans_accident = (today - oldest).days
                result.dernier_accident_date = "Aucun accident enregistré"

    # ------------------------------------------------------------------
    # 7. Évolution de la conformité (par date_audit triée)
    # ------------------------------------------------------------------
    dated_subs = []
    for s in filtered_submissions:
        d = _parse_date_audit(s.date_audit)
        if d:
            dated_subs.append((d, s.taux_conformite))
    dated_subs.sort(key=lambda x: x[0])

    # Grouper par semaine ou par soumission (limiter aux 10 dernières entrées)
    if dated_subs:
        last_entries = dated_subs[-10:]
        for d, tc in last_entries:
            result.conformite_labels.append(d.strftime("%d/%m"))
            result.conformite_values.append(round(tc, 1))

        # Conformité de la dernière tournée
        result.conformite_derniere_tournee = last_entries[-1][1]
        if len(last_entries) >= 2:
            result.conformite_variation = round(
                last_entries[-1][1] - last_entries[-2][1], 1
            )

    # ------------------------------------------------------------------
    # 8. Radar des 7 thématiques HSE (agrégation par section_id)
    # ------------------------------------------------------------------
    section_scores: Dict[int, List[int]] = {i: [] for i in range(1, 8)}

    # Items d'audit
    audit_items = db.query(AuditHSEItem).filter(
        AuditHSEItem.audit_id.in_(submission_ids)
    ).all() if submission_ids else []
    for item in audit_items:
        sid = item.section_id
        if 1 <= sid <= 7 and item.conformite >= 0:
            section_scores[sid].append(item.conformite)

    # Items de tournée
    tournee_items = db.query(TourneeHSEItem).filter(
        TourneeHSEItem.tournee_id.in_(submission_ids)
    ).all() if submission_ids else []
    for item in tournee_items:
        sid = item.section_id
        if 1 <= sid <= 7 and item.conformite >= 0:
            section_scores[sid].append(item.conformite)

    for sid in range(1, 8):
        result.radar_labels.append(SECTION_LABELS.get(sid, f"Section {sid}"))
        scores = section_scores[sid]
        if scores:
            result.radar_scores.append(round(sum(scores) / len(scores) * 100, 1))
        else:
            result.radar_scores.append(0.0)

    # ------------------------------------------------------------------
    # 9. Conformité par secteur (graphique barres)
    # ------------------------------------------------------------------
    secteur_map: Dict[str, List[float]] = {}
    for s in filtered_submissions:
        sec = s.secteur or "Autre"
        secteur_map.setdefault(sec, []).append(s.taux_conformite)

    for sec in sorted(secteur_map.keys()):
        scores = secteur_map[sec]
        result.secteur_labels.append(sec)
        result.secteur_values.append(round(sum(scores) / len(scores), 1))

    # ------------------------------------------------------------------
    # 10. Tableau des actions en retard détaillées
    # ------------------------------------------------------------------
    retard_actions = []

    # Items d'audit en retard
    for item in audit_items:
        if item.etat == "en_retard" and item.conformite == 0:
            # Trouver la soumission parente
            parent = next((s for s in filtered_submissions if s.id == item.audit_id), None)
            delai_date = _parse_date_audit(item.delai) if item.delai else None
            retard_jours = (today - delai_date).days if delai_date and delai_date < today else 0

            retard_actions.append({
                "id": item.id,
                "ref": parent.reference if parent else "N/A",
                "source": "Audit HSE (FGSI-001)",
                "secteur": parent.secteur if parent else "N/A",
                "constat": item.constat or "Non-conformité détectée",
                "action": item.action_corrective or "Action à définir",
                "responsable": item.responsable or "Non assigné",
                "delai": item.delai or "Non défini",
                "retardJours": retard_jours,
                "priorite": "Critique" if retard_jours > 10 else ("Haute" if retard_jours > 5 else "Moyenne"),
            })

    # Items de tournée en retard
    for item in tournee_items:
        if item.etat == "en_retard" and item.conformite == 0:
            parent = next((s for s in filtered_submissions if s.id == item.tournee_id), None)
            delai_date = _parse_date_audit(item.delai) if item.delai else None
            retard_jours = (today - delai_date).days if delai_date and delai_date < today else 0

            retard_actions.append({
                "id": item.id,
                "ref": parent.reference if parent else "N/A",
                "source": "Tournée HSE (FGSI-010)",
                "secteur": parent.secteur if parent else "N/A",
                "constat": item.constat or "Non-conformité détectée",
                "action": item.action_corrective or "Action à définir",
                "responsable": item.responsable or "Non assigné",
                "delai": item.delai or "Non défini",
                "retardJours": retard_jours,
                "priorite": "Critique" if retard_jours > 10 else ("Haute" if retard_jours > 5 else "Moyenne"),
            })

    # Trier par nombre de jours de retard décroissant
    retard_actions.sort(key=lambda x: x["retardJours"], reverse=True)
    result.actions_retard_details = retard_actions

    return result

