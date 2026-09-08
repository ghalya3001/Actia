"""
===============================================================================
SERVICE DE CALCUL DES KPIS ET SNAPSHOTS DASHBOARD (KPI_SERVICE.PY)
===============================================================================
Ce service implémente la méthode choisie : recalcul automatique après chaque
POST / PUT / DELETE de formulaire, stockage dans la table `kpi_snapshots`,
et alimentation instantanée du Dashboard.
===============================================================================
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.submission import (
    FormSubmission,
    AuditHSESubmission,
    TourneeHSESubmission,
    PermisTravailSubmission,
)
from app.models.dashboard import KPIDefinition, KPISnapshot, DashboardWidget
from app.schemas.audit import HSEAuditStats

logger = logging.getLogger(__name__)

# Définitions standard des KPIs insérées au démarrage
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


class KPIService:

    @staticmethod
    def ensure_default_kpi_definitions(db: Session):
        """Initialise le catalogue kpi_definitions s'il est vide."""
        try:
            count = db.query(KPIDefinition).count()
            if count == 0:
                for d in DEFAULT_KPI_DEFINITIONS:
                    kpi = KPIDefinition(**d)
                    db.add(kpi)
                db.commit()
                logger.info("[KPI Service] Catalogue de KPI par défaut initialisé.")
        except Exception as e:
            db.rollback()
            logger.warning(f"[KPI Service] Impossible d'initialiser les KPIs par défaut: {e}")

    @classmethod
    def recalculate_kpis_for_user(cls, user_id: int):
        """
        Recalcule tous les KPIs impactés pour l'utilisateur en tâche de fond (BackgroundTasks).
        Ouvre sa propre session de base de données pour une exécution asynchrone sûre.
        """
        db: Session = SessionLocal()
        try:
            cls.ensure_default_kpi_definitions(db)

            # 1. Calculs sur form_submissions
            submissions = db.query(FormSubmission).filter(FormSubmission.user_id == user_id).all()
            total_subs = len(submissions)

            if total_subs > 0:
                avg_conf = sum(s.taux_conformite for s in submissions) / total_subs
            else:
                avg_conf = 0.0

            # 2. Calculs des actions (Audit + Tournée)
            audits = db.query(AuditHSESubmission).filter(AuditHSESubmission.user_id == user_id).all()
            tournees = db.query(TourneeHSESubmission).filter(TourneeHSESubmission.user_id == user_id).all()

            soldee = sum(a.count_soldee for a in audits) + sum(t.count_soldee for t in tournees)
            non_engagee = sum(a.count_non_engagee for a in audits) + sum(t.count_non_engagee for t in tournees)
            en_cours = sum(a.count_en_cours for a in audits) + sum(t.count_en_cours for t in tournees)
            en_retard = sum(a.count_en_retard for a in audits) + sum(t.count_en_retard for t in tournees)

            # 3. Calculs des permis
            permis = db.query(PermisTravailSubmission).filter(PermisTravailSubmission.user_id == user_id).all()
            total_permis = sum(p.nb_plan_prevention + p.nb_permis_hauteur + p.nb_permis_feu for p in permis)

            # 4. Calcul de la conformité par secteur
            secteur_map: Dict[str, List[float]] = {}
            for s in submissions:
                sec = s.secteur or "Autre"
                secteur_map.setdefault(sec, []).append(s.taux_conformite)

            secteur_avg = {sec: round(sum(scores) / len(scores), 1) for sec, scores in secteur_map.items()}

            # 5. Préparation des valeurs à enregistrer dans kpi_snapshots
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

            # 6. UPSERT dans kpi_snapshots
            for kpi_name, (val, breakdown) in kpi_values.items():
                kpi_def = db.query(KPIDefinition).filter(KPIDefinition.name == kpi_name).first()
                if not kpi_def:
                    continue

                snapshot = db.query(KPISnapshot).filter(
                    KPISnapshot.kpi_id == kpi_def.id,
                    KPISnapshot.user_id == user_id
                ).first()

                if snapshot:
                    snapshot.value = val
                    snapshot.breakdown_data = breakdown
                    snapshot.computed_at = now
                else:
                    snapshot = KPISnapshot(
                        kpi_id=kpi_def.id,
                        user_id=user_id,
                        value=val,
                        breakdown_data=breakdown,
                        computed_at=now,
                    )
                    db.add(snapshot)

            db.commit()
            logger.info(f"[KPI Service] Recalcul terminé avec succès pour user_id={user_id}")

        except Exception as e:
            db.rollback()
            logger.error(f"[KPI Service] Erreur lors du recalcul des KPIs pour user_id={user_id}: {e}")
        finally:
            db.close()

    @classmethod
    def get_user_stats(cls, db: Session, user_id: int) -> HSEAuditStats:
        """
        Retourne instantanément les statistiques sous forme HSEAuditStats.
        Lit en priorité kpi_snapshots. Si absent, déclenche un calcul immédiat.
        """
        # Récupération depuis kpi_snapshots
        snapshots = db.query(KPISnapshot, KPIDefinition.name).join(
            KPIDefinition, KPISnapshot.kpi_id == KPIDefinition.id
        ).filter(KPISnapshot.user_id == user_id).all()

        snap_dict = {name: snap.value for snap, name in snapshots}

        if "total_audits" in snap_dict and "avg_conformite" in snap_dict:
            # Distribution des actions
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

        # Calcul direct si pas encore de snapshots
        submissions = db.query(FormSubmission).filter(FormSubmission.user_id == user_id).all()
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
        audits = db.query(AuditHSESubmission).filter(AuditHSESubmission.user_id == user_id).all()
        tournees = db.query(TourneeHSESubmission).filter(TourneeHSESubmission.user_id == user_id).all()

        soldee = sum(a.count_soldee for a in audits) + sum(t.count_soldee for t in tournees)
        non_engagee = sum(a.count_non_engagee for a in audits) + sum(t.count_non_engagee for t in tournees)
        en_cours = sum(a.count_en_cours for a in audits) + sum(t.count_en_cours for t in tournees)
        en_retard = sum(a.count_en_retard for a in audits) + sum(t.count_en_retard for t in tournees)

        # Déclenchement asynchrone du snapshot pour la prochaine fois
        try:
            cls.recalculate_kpis_for_user(user_id)
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
