"""
===============================================================================
SERVICE DE GESTION DES SOUMISSIONS HSE (SUBMISSION_SERVICE.PY)
===============================================================================
Ce service fait la passerelle entre le contrat d'API / frontend (qui envoie
un objet complet avec items_data) et les tables relationnelles normalisées
selon le diagramme de classes Mermaid :
  - Décomposition à l'écriture (INSERT / UPDATE)
  - Reconstitution transparente à la lecture (GET)
  - Gestion des photos associées
===============================================================================
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.models.submission import (
    FormSubmission,
    AuditHSESubmission,
    AuditHSEItem,
    TourneeHSESubmission,
    TourneeHSEItem,
    PermisTravailSubmission,
    PhotoStorage,
)
from app.schemas.audit import HSEAuditCreate, HSEAuditUpdate


# Mapping pour convertir les états d'action entre le frontend et la base
ETAT_NORMALIZE = {
    "non engagée": "non_engagee",
    "non engagee": "non_engagee",
    "en cours": "en_cours",
    "soldée": "soldee",
    "soldee": "soldee",
    "en retard": "en_retard",
}

ETAT_DISPLAY = {
    "non_engagee": "Non engagée",
    "en_cours": "En cours",
    "soldee": "Soldée",
    "en_retard": "En retard",
}


class SubmissionService:

    @staticmethod
    def _normalize_etat(etat_str: Optional[str]) -> str:
        if not etat_str:
            return "non_engagee"
        lower = etat_str.strip().lower()
        return ETAT_NORMALIZE.get(lower, "non_engagee")

    @staticmethod
    def _display_etat(etat_db: Optional[str]) -> str:
        if not etat_db:
            return "Non engagée"
        return ETAT_DISPLAY.get(etat_db, etat_db)

    @classmethod
    def create_submission(cls, db: Session, audit_in: HSEAuditCreate, user_id: int) -> Dict[str, Any]:
        """
        Crée une nouvelle soumission et la ventile dans les tables relationnelles appropriées.
        """
        form_type = audit_in.form_type
        # Normalisation du type de formulaire
        if form_type in ("audit_hse", "audit_hse_complet"):
            target_type = "audit_hse"
        elif form_type == "tournee_hse":
            target_type = "tournee_hse"
        elif form_type == "permis_travail":
            target_type = "permis_travail"
        else:
            target_type = "audit_hse"

        # 1. Instanciation de la classe enfant spécifique (Joined Table Inheritance)
        if target_type == "audit_hse":
            submission = AuditHSESubmission(
                user_id=user_id,
                form_type=target_type,
                reference=audit_in.reference,
                secteur=audit_in.secteur,
                intervenants=audit_in.intervenants,
                date_audit=audit_in.date_audit,
                taux_conformite=audit_in.taux_conformite,
                commentaires_generaux=audit_in.commentaires_generaux,
                total_conforme=audit_in.total_conforme,
                total_non_conforme=audit_in.total_non_conforme,
                total_na=audit_in.total_na,
                count_soldee=audit_in.count_soldee,
                count_non_engagee=audit_in.count_non_engagee,
                count_en_cours=audit_in.count_en_cours,
                count_en_retard=audit_in.count_en_retard,
            )
            db.add(submission)
            db.flush()  # Pour obtenir submission.id

            # 2. Décomposition des items relationnels
            cls._save_audit_items(db, submission.id, audit_in.items_data)

        elif target_type == "tournee_hse":
            submission = TourneeHSESubmission(
                user_id=user_id,
                form_type=target_type,
                reference=audit_in.reference,
                secteur=audit_in.secteur,
                intervenants=audit_in.intervenants,
                date_audit=audit_in.date_audit,
                taux_conformite=audit_in.taux_conformite,
                commentaires_generaux=audit_in.commentaires_generaux,
                total_conforme=audit_in.total_conforme,
                total_non_conforme=audit_in.total_non_conforme,
                total_na=audit_in.total_na,
                count_soldee=audit_in.count_soldee,
                count_non_engagee=audit_in.count_non_engagee,
                count_en_cours=audit_in.count_en_cours,
                count_en_retard=audit_in.count_en_retard,
            )
            db.add(submission)
            db.flush()

            cls._save_tournee_items(db, submission.id, audit_in.items_data)

        elif target_type == "permis_travail":
            items_d = audit_in.items_data or {}
            submission = PermisTravailSubmission(
                user_id=user_id,
                form_type=target_type,
                reference=audit_in.reference,
                secteur=audit_in.secteur,
                intervenants=audit_in.intervenants,
                date_audit=audit_in.date_audit,
                taux_conformite=audit_in.taux_conformite or 100.0,
                commentaires_generaux=audit_in.commentaires_generaux,
                nb_plan_prevention=int(items_d.get("plan_prevention") or 0),
                nb_permis_hauteur=int(items_d.get("permis_hauteur") or 0),
                nb_permis_feu=int(items_d.get("permis_feu") or 0),
                remarques_specifiques=str(items_d.get("remarques") or ""),
            )
            db.add(submission)
            db.flush()

        db.commit()
        db.refresh(submission)
        return cls.submission_to_dict(submission)

    @classmethod
    def _save_audit_items(cls, db: Session, audit_id: int, items_data: Dict[str, Any]):
        """Enregistre les items de l'audit HSE dans audit_hse_items"""
        if not items_data or not isinstance(items_data, dict):
            return

        for q_key, val_data in items_data.items():
            try:
                q_id = int(q_key)
            except ValueError:
                continue

            if not isinstance(val_data, dict):
                val_data = {"val": val_data}

            raw_val = val_data.get("val")
            if raw_val == "NA":
                conf = -1
            elif raw_val in (1, "1"):
                conf = 1
            else:
                conf = 0

            photo = val_data.get("photo")
            etat = cls._normalize_etat(val_data.get("etat"))

            item = AuditHSEItem(
                audit_id=audit_id,
                question_id=q_id,
                conformite=conf,
                constat=val_data.get("constat"),
                photo_url=photo,
                action_corrective=val_data.get("action"),
                responsable=val_data.get("resp"),
                delai=val_data.get("delai"),
                etat=etat,
                commentaire=val_data.get("comm"),
            )
            db.add(item)
            db.flush()

            # Si une photo est fournie, l'enregistrer également dans photo_storage
            if photo:
                photo_entry = PhotoStorage(
                    item_id=item.id,
                    item_type="audit_hse",
                    file_path=photo[:200] if len(photo) > 200 else photo,
                    original_filename=f"audit_{audit_id}_q{q_id}.jpg"
                )
                db.add(photo_entry)

    @classmethod
    def _save_tournee_items(cls, db: Session, tournee_id: int, items_data: Dict[str, Any]):
        """Enregistre les items de la Tournée HSE dans tournee_hse_items"""
        if not items_data or not isinstance(items_data, dict):
            return

        for q_key, val_data in items_data.items():
            try:
                q_id = int(q_key)
            except ValueError:
                continue

            if not isinstance(val_data, dict):
                val_data = {"val": val_data}

            raw_val = val_data.get("val")
            if raw_val == "NA":
                conf = -1
            elif raw_val in (1, "1"):
                conf = 1
            else:
                conf = 0

            photo = val_data.get("photo")
            etat = cls._normalize_etat(val_data.get("etat"))

            item = TourneeHSEItem(
                tournee_id=tournee_id,
                question_id=q_id,
                conformite=conf,
                constat=val_data.get("constat"),
                photo_url=photo,
                action_corrective=val_data.get("action"),
                responsable=val_data.get("resp"),
                delai=val_data.get("delai"),
                etat=etat,
                commentaire=val_data.get("comm"),
            )
            db.add(item)
            db.flush()

            if photo:
                photo_entry = PhotoStorage(
                    item_id=item.id,
                    item_type="tournee_hse",
                    file_path=photo[:200] if len(photo) > 200 else photo,
                    original_filename=f"tournee_{tournee_id}_q{q_id}.jpg"
                )
                db.add(photo_entry)

    @classmethod
    def get_submission_by_id(cls, db: Session, audit_id: int, user_id: int) -> Dict[str, Any]:
        """Récupère une soumission et reconstitue le dictionnaire items_data."""
        sub = db.query(FormSubmission).filter(
            FormSubmission.id == audit_id,
            FormSubmission.user_id == user_id
        ).first()

        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit introuvable avec l'ID {audit_id}."
            )
        return cls.submission_to_dict(sub)

    @classmethod
    def get_all_submissions(
        cls,
        db: Session,
        user_id: int,
        date_audit: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        form_type: Optional[str] = None,
        secteur: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Récupère toutes les soumissions de l'utilisateur avec filtres."""
        query = db.query(FormSubmission).filter(FormSubmission.user_id == user_id)

        if date_audit:
            query = query.filter(FormSubmission.date_audit == date_audit)
        if date_from:
            query = query.filter(FormSubmission.date_audit >= date_from)
        if date_to:
            query = query.filter(FormSubmission.date_audit <= date_to)
        if form_type:
            if form_type in ("audit_hse", "audit_hse_complet"):
                query = query.filter(FormSubmission.form_type.in_(["audit_hse", "audit_hse_complet"]))
            else:
                query = query.filter(FormSubmission.form_type == form_type)
        if secteur:
            query = query.filter(
                or_(
                    FormSubmission.secteur.ilike(f"%{secteur}%"),
                    FormSubmission.intervenants.ilike(f"%{secteur}%")
                )
            )

        submissions = query.order_by(FormSubmission.created_at.desc()).all()
        return [cls.submission_to_dict(s) for s in submissions]

    @classmethod
    def update_submission(
        cls, db: Session, audit_id: int, audit_in: HSEAuditUpdate, user_id: int
    ) -> Dict[str, Any]:
        """Met à jour une soumission existante et synchronise ses items."""
        sub = db.query(FormSubmission).filter(
            FormSubmission.id == audit_id,
            FormSubmission.user_id == user_id
        ).first()

        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit introuvable avec l'ID {audit_id}."
            )

        # Mise à jour des champs communs
        update_data = audit_in.model_dump(exclude_unset=True)
        for field in ("reference", "secteur", "intervenants", "date_audit", "commentaires_generaux", "taux_conformite"):
            if field in update_data and update_data[field] is not None:
                setattr(sub, field, update_data[field])

        # Mise à jour des compteurs sur l'enfant
        if isinstance(sub, (AuditHSESubmission, TourneeHSESubmission)):
            for field in ("total_conforme", "total_non_conforme", "total_na", "count_soldee", "count_non_engagee", "count_en_cours", "count_en_retard"):
                if field in update_data and update_data[field] is not None:
                    setattr(sub, field, update_data[field])

        # Synchronisation des items si fournis
        if "items_data" in update_data and update_data["items_data"] is not None:
            if isinstance(sub, AuditHSESubmission):
                # Supprimer les anciens items et recréer
                db.query(AuditHSEItem).filter(AuditHSEItem.audit_id == sub.id).delete()
                cls._save_audit_items(db, sub.id, update_data["items_data"])
            elif isinstance(sub, TourneeHSESubmission):
                db.query(TourneeHSEItem).filter(TourneeHSEItem.tournee_id == sub.id).delete()
                cls._save_tournee_items(db, sub.id, update_data["items_data"])
            elif isinstance(sub, PermisTravailSubmission):
                items_d = update_data["items_data"]
                if "plan_prevention" in items_d:
                    sub.nb_plan_prevention = int(items_d["plan_prevention"] or 0)
                if "permis_hauteur" in items_d:
                    sub.nb_permis_hauteur = int(items_d["permis_hauteur"] or 0)
                if "permis_feu" in items_d:
                    sub.nb_permis_feu = int(items_d["permis_feu"] or 0)
                if "remarques" in items_d:
                    sub.remarques_specifiques = str(items_d["remarques"] or "")

        db.commit()
        db.refresh(sub)
        return cls.submission_to_dict(sub)

    @classmethod
    def delete_submission(cls, db: Session, audit_id: int, user_id: int) -> bool:
        """Supprime une soumission (les tables filles et items sont supprimés en cascade)."""
        sub = db.query(FormSubmission).filter(
            FormSubmission.id == audit_id,
            FormSubmission.user_id == user_id
        ).first()

        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit introuvable avec l'ID {audit_id}."
            )

        db.delete(sub)
        db.commit()
        return True

    @classmethod
    def submission_to_dict(cls, sub: FormSubmission) -> Dict[str, Any]:
        """
        Reconstitue l'objet retourné exactement au format HSEAuditOut attendu
        par le frontend Vue (avec le dictionnaire items_data complet).
        """
        data: Dict[str, Any] = {
            "id": sub.id,
            "reference": sub.reference,
            "form_type": sub.form_type,
            "secteur": sub.secteur,
            "intervenants": sub.intervenants,
            "date_audit": sub.date_audit,
            "commentaires_generaux": sub.commentaires_generaux,
            "taux_conformite": sub.taux_conformite,
            "user_id": sub.user_id,
            "created_at": sub.created_at,
        }

        # Données spécifiques selon le type
        if isinstance(sub, AuditHSESubmission):
            data["total_conforme"] = sub.total_conforme
            data["total_non_conforme"] = sub.total_non_conforme
            data["total_na"] = sub.total_na
            data["count_soldee"] = sub.count_soldee
            data["count_non_engagee"] = sub.count_non_engagee
            data["count_en_cours"] = sub.count_en_cours
            data["count_en_retard"] = sub.count_en_retard

            # Reconstitution de items_data
            items_dict = {}
            for it in (sub.items or []):
                val = 1 if it.conformite == 1 else (0 if it.conformite == 0 else "NA")
                items_dict[str(it.question_id)] = {
                    "val": val,
                    "constat": it.constat or "",
                    "photo": it.photo_url or "",
                    "action": it.action_corrective or "",
                    "resp": it.responsable or "",
                    "delai": it.delai or "",
                    "etat": cls._display_etat(it.etat),
                    "comm": it.commentaire or "",
                }
            data["items_data"] = items_dict

        elif isinstance(sub, TourneeHSESubmission):
            data["total_conforme"] = sub.total_conforme
            data["total_non_conforme"] = sub.total_non_conforme
            data["total_na"] = sub.total_na
            data["count_soldee"] = sub.count_soldee
            data["count_non_engagee"] = sub.count_non_engagee
            data["count_en_cours"] = sub.count_en_cours
            data["count_en_retard"] = sub.count_en_retard

            items_dict = {}
            for it in (sub.items or []):
                val = 1 if it.conformite == 1 else (0 if it.conformite == 0 else "NA")
                items_dict[str(it.question_id)] = {
                    "val": val,
                    "constat": it.constat or "",
                    "photo": it.photo_url or "",
                    "action": it.action_corrective or "",
                    "resp": it.responsable or "",
                    "delai": it.delai or "",
                    "etat": cls._display_etat(it.etat),
                    "comm": it.commentaire or "",
                }
            data["items_data"] = items_dict

        elif isinstance(sub, PermisTravailSubmission):
            data["total_conforme"] = 0
            data["total_non_conforme"] = 0
            data["total_na"] = 0
            data["count_soldee"] = 0
            data["count_non_engagee"] = 0
            data["count_en_cours"] = 0
            data["count_en_retard"] = 0

            data["items_data"] = {
                "plan_prevention": sub.nb_plan_prevention,
                "permis_hauteur": sub.nb_permis_hauteur,
                "permis_feu": sub.nb_permis_feu,
                "remarques": sub.remarques_specifiques or "",
            }
        else:
            data["total_conforme"] = 0
            data["total_non_conforme"] = 0
            data["total_na"] = 0
            data["count_soldee"] = 0
            data["count_non_engagee"] = 0
            data["count_en_cours"] = 0
            data["count_en_retard"] = 0
            data["items_data"] = {}

        return data
