"""
===============================================================================
SERVICE DE CALCUL DES KPIS ET SNAPSHOTS DU DASHBOARD (KPI_SERVICE.PY)
===============================================================================
Rôle :
  Implémente le moteur décisionnel et analytique pour le tableau de bord HSE :
  - Initialisation au démarrage du catalogue d'indicateurs configurables (`kpi_definitions`).
  - Recalcul complet et asynchrone des indicateurs (`recalculate_kpis_for_user`)
    déclenché après chaque ajout, modification ou suppression de formulaire.
  - Mise en cache des résultats sous forme de snapshots (`kpi_snapshots`)
    afin de garantir un temps de réponse instantané (< 10 ms) pour le frontend.
  - Distribution par secteur, statuts des actions correctives et cumul des permis.

Équipe de maintenance :
  - La méthode `recalculate_kpis_for_user()` ouvre sa propre session BDD indépendante
    (`SessionLocal()`), ce qui la rend parfaitement compatible avec l'exécution en arrière-plan
    FastAPI (`BackgroundTasks`) sans risque de concurrence de threads.
===============================================================================
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.submission import (
    FormSubmission,
    AuditHSESubmission,
    TourneeHSESubmission,
    PermisTravailSubmission,
)
from app.models.dashboard import KPIDefinition, KPISnapshot, DashboardWidget
from app.schemas.audit import HSEAuditStats

logger = logging.getLogger(__name__)

# =============================================================================
# 1. CATALOGUE PAR DÉFAUT DES INDICATEURS SYSTÈME HSE
# =============================================================================
# Ces définitions sont injectées automatiquement dans 'kpi_definitions'
# si la table est vide lors du premier lancement de l'application.
DEFAULT_KPI_DEFINITIONS = [
    {
        "name": "total_audits",
        "label": "Total Audits & Tournées Réalisés",
        "form_type": "all",
        "source_table": "form_submissions",
        "aggregation": "COUNT",
        "chart_type": "card",
        "display_order": 1,
    },
    {
        "name": "avg_conformite",
        "label": "Taux Moyen de Conformité HSE",
        "form_type": "all",
        "source_table": "form_submissions",
        "aggregation": "AVG",
        "chart_type": "card",
        "display_order": 2,
    },
    {
        "name": "actions_soldee",
        "label": "Actions Soldées",
        "form_type": "all",
        "source_table": "audit_hse_submissions",
        "aggregation": "SUM",
        "chart_type": "card",
        "display_order": 3,
    },
    {
        "name": "actions_en_retard",
        "label": "Actions En Retard",
        "form_type": "all",
        "source_table": "audit_hse_submissions",
        "aggregation": "SUM",
        "chart_type": "card",
        "display_order": 4,
    },
    {
        "name": "actions_distribution",
        "label": "Répartition des Actions Correctives",
        "form_type": "all",
        "source_table": "audit_hse_submissions",
        "aggregation": "COUNT_FILTERED",
        "chart_type": "doughnut",
        "display_order": 5,
    },
    {
        "name": "conformite_par_secteur",
        "label": "Taux de Conformité par Secteur",
        "form_type": "all",
        "source_table": "form_submissions",
        "aggregation": "AVG_GROUP_BY",
        "group_by_column": "secteur",
        "chart_type": "bar",
        "display_order": 6,
    },
    {
        "name": "total_permis",
        "label": "Permis de Travail Émis",
        "form_type": "permis_travail",
        "source_table": "permis_travail_submissions",
        "aggregation": "SUM",
        "chart_type": "card",
        "display_order": 7,
    },
]


# =============================================================================
# 2. SERVICE PRINCIPAL : KPISERVICE
# =============================================================================
class KPIService:
    """
    Classe de service fournissant les opérations de calcul et de restitution
    des indicateurs de performance clés (KPIs) pour le tableau de bord.
    """

    @staticmethod
    def ensure_default_kpi_definitions(db: Session):
        """
        Vérifie l'existence des indicateurs dans la table `kpi_definitions`.
        Si la table est vide, peuple automatiquement les indicateurs par défaut.

        Args:
            db (Session): Session de base de données active.
        """
        try:
            # Comptage des définitions déjà enregistrées
            count = db.query(KPIDefinition).count()
            if count == 0:
                # Insertion séquentielle des indicateurs par défaut
                for d in DEFAULT_KPI_DEFINITIONS:
                    kpi = KPIDefinition(**d)
                    db.add(kpi)
                db.commit()
                logger.info("[KPI Service] Catalogue de KPI par défaut initialisé.")
        except Exception as e:
            db.rollback()
            logger.warning(f"[KPI Service] Impossible d'initialiser les KPIs par défaut: {e}")

    @classmethod
    def recalculate_kpis_for_user(cls, user_id: Optional[int] = None):
        """
        Recalcule tous les KPIs de façon centralisée à l'échelle de l'usine entière
        et stocke les résultats consolidés dans la table cache `kpi_snapshots`.
        Toutes les fiches remplies par n'importe quel utilisateur alimentent le même Dashboard.
        Les snapshots sont synchronisés pour le global (user_id=None) ainsi que pour tous les utilisateurs.
        """
        # Ouverture d'une session indépendante et dédiée à cette exécution asynchrone
        db = SessionLocal()
        try:
            # Vérification de sécurité du catalogue de base
            cls.ensure_default_kpi_definitions(db)

            # --- Étape 1 : Calcul des moyennes globales sur form_submissions (Centralisé usine) ---
            submissions = db.query(FormSubmission).all()
            total_subs = len(submissions)

            if total_subs > 0:
                avg_conf = sum(s.taux_conformite for s in submissions) / total_subs
            else:
                avg_conf = 0.0

            # --- Étape 2 : Agrégation des actions correctives (Audits + Tournées) ---
            audits = db.query(AuditHSESubmission).all()
            tournees = db.query(TourneeHSESubmission).all()

            # Cumul des actions par statut
            soldee = sum(a.count_soldee for a in audits) + sum(t.count_soldee for t in tournees)
            non_engagee = sum(a.count_non_engagee for a in audits) + sum(t.count_non_engagee for t in tournees)
            en_cours = sum(a.count_en_cours for a in audits) + sum(t.count_en_cours for t in tournees)
            en_retard = sum(a.count_en_retard for a in audits) + sum(t.count_en_retard for t in tournees)

            # --- Étape 3 : Cumul des autorisations et permis de travail ---
            permis = db.query(PermisTravailSubmission).all()
            total_permis = sum(p.nb_plan_prevention + p.nb_permis_hauteur + p.nb_permis_feu for p in permis)

            # --- Étape 4 : Répartition et moyenne de conformité par atelier / secteur ---
            secteur_map: Dict[str, List[float]] = {}
            for s in submissions:
                sec = s.secteur or "Autre"
                secteur_map.setdefault(sec, []).append(s.taux_conformite)

            # Calcul de la moyenne arrondie par secteur
            secteur_avg = {sec: round(sum(scores) / len(scores), 1) for sec, scores in secteur_map.items()}

            # --- Étape 5 : Préparation de la structure des snapshots à insérer / mettre à jour ---
            kpi_values = {
                "total_audits": (float(total_subs), None),
                "avg_conformite": (round(avg_conf, 1), None),
                "actions_soldee": (float(soldee), None),
                "actions_en_retard": (float(en_retard), None),
                "actions_distribution": (
                    float(soldee + non_engagee + en_cours + en_retard),
                    {
                        "soldee": soldee,
                        "non_engagee": non_engagee,
                        "en_cours": en_cours,
                        "en_retard": en_retard,
                    },
                ),
                "conformite_par_secteur": (round(avg_conf, 1), secteur_avg),
                "total_permis": (float(total_permis), None),
            }

            now = datetime.now(timezone.utc)

            # Liste des cibles à synchroniser : None (vue globale) + tous les utilisateurs enregistrés
            target_user_ids: List[Optional[int]] = [None]
            all_users = db.query(User.id).all()
            for u in all_users:
                target_user_ids.append(u[0])
            if user_id and user_id not in target_user_ids:
                target_user_ids.append(user_id)

            # --- Étape 6 : UPSERT dans kpi_snapshots pour chaque cible ---
            for uid in target_user_ids:
                for kpi_name, (val, breakdown) in kpi_values.items():
                    kpi_def = db.query(KPIDefinition).filter(KPIDefinition.name == kpi_name).first()
                    if not kpi_def:
                        continue

                    # Recherche d'un snapshot existant pour ce KPI et cette cible
                    query = db.query(KPISnapshot).filter(KPISnapshot.kpi_id == kpi_def.id)
                    if uid is None:
                        snapshot = query.filter(KPISnapshot.user_id.is_(None)).first()
                    else:
                        snapshot = query.filter(KPISnapshot.user_id == uid).first()

                    if snapshot:
                        snapshot.value = val
                        snapshot.breakdown_data = breakdown
                        snapshot.computed_at = now
                    else:
                        snapshot = KPISnapshot(
                            kpi_id=kpi_def.id,
                            user_id=uid,
                            value=val,
                            breakdown_data=breakdown,
                            computed_at=now,
                        )
                        db.add(snapshot)

            db.commit()
            logger.info("[KPI Service] Recalcul centralisé terminé avec succès pour toute l'usine")

        except Exception as e:
            db.rollback()
            logger.error(f"[KPI Service] Erreur lors du recalcul centralisé des KPIs: {e}")
        finally:
            db.close()

    @classmethod
    def get_user_stats(cls, db: Any, user_id: Optional[int] = None) -> HSEAuditStats:
        """
        Retourne instantanément les statistiques consolidées de l'usine entière.
        Lit en priorité le cache `kpi_snapshots`. Si les snapshots sont absents,
        calcule à la volée sur toutes les fiches de l'usine.
        """
        # --- Stratégie 1 : Lecture haute performance depuis le cache kpi_snapshots ---
        query = db.query(KPISnapshot, KPIDefinition.name).join(
            KPIDefinition, KPISnapshot.kpi_id == KPIDefinition.id
        )
        if user_id:
            snapshots = query.filter(or_(KPISnapshot.user_id == user_id, KPISnapshot.user_id.is_(None))).all()
        else:
            snapshots = query.filter(KPISnapshot.user_id.is_(None)).all()

        snap_dict = {name: snap.value for snap, name in snapshots}

        if "total_audits" in snap_dict and "avg_conformite" in snap_dict:
            dist_snap = next((snap for snap, name in snapshots if name == "actions_distribution"), None)
            dist_json = dist_snap.breakdown_data if (dist_snap and dist_snap.breakdown_data) else {}

            return HSEAuditStats(
                total_audits=int(snap_dict.get("total_audits", 0)),
                avg_conformite=float(snap_dict.get("avg_conformite", 0.0)),
                total_actions_soldee=int(dist_json.get("soldee", snap_dict.get("actions_soldee", 0))),
                total_actions_non_engagee=int(dist_json.get("non_engagee", 0)),
                total_actions_en_cours=int(dist_json.get("en_cours", 0)),
                total_actions_en_retard=int(dist_json.get("en_retard", snap_dict.get("actions_en_retard", 0))),
            )

        # --- Stratégie 2 : Calcul direct de secours sur TOUTES les fiches de l'usine ---
        submissions = db.query(FormSubmission).all()
        total_audits = len(submissions)
        if total_audits == 0:
            return HSEAuditStats(
                total_audits=0,
                avg_conformite=0.0,
                total_actions_soldee=0,
                total_actions_non_engagee=0,
                total_actions_en_cours=0,
                total_actions_en_retard=0,
            )

        avg_conf = sum(s.taux_conformite for s in submissions) / total_audits
        audits = db.query(AuditHSESubmission).all()
        tournees = db.query(TourneeHSESubmission).all()

        soldee = sum(a.count_soldee for a in audits) + sum(t.count_soldee for t in tournees)
        non_engagee = sum(a.count_non_engagee for a in audits) + sum(t.count_non_engagee for t in tournees)
        en_cours = sum(a.count_en_cours for a in audits) + sum(t.count_en_cours for t in tournees)
        en_retard = sum(a.count_en_retard for a in audits) + sum(t.count_en_retard for t in tournees)

        # Déclenchement silencieux du recalcul asynchrone pour alimenter le cache au prochain appel
        try:
            cls.recalculate_kpis_for_user()
        except Exception:
            pass

        return HSEAuditStats(
            total_audits=total_audits,
            avg_conformite=round(avg_conf, 1),
            total_actions_soldee=soldee,
            total_actions_non_engagee=non_engagee,
            total_actions_en_cours=en_cours,
            total_actions_en_retard=en_retard,
        )
