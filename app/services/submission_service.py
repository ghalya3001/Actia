"""
===============================================================================
SERVICE DE GESTION DES SOUMISSIONS HSE (SUBMISSION_SERVICE.PY)
===============================================================================
Rôle :
  Fait la passerelle complète entre le contrat d'API / frontend Vue 3 (qui échange
  un objet JSON consolidé avec le dictionnaire `items_data`) et les tables
  relationnelles PostgreSQL normalisées (modèle Joined Table Inheritance) :
  
  1. Écriture (CREATE / UPDATE) :
     - Décomposition fine de la soumission dans la table mère (`form_submissions`)
       et la table fille spécialisée (`audit_hse_submissions`, `tournee_hse_submissions`,
       `permis_travail_submissions`, `accident_travail_submissions`).
     - Éclatement des points de contrôle dans les tables d'items relationnels
       (`audit_hse_items`, `tournee_hse_items`, `accident_travail_monthly_items`).
     - Enregistrement des photographies de preuves dans `photo_storage`.
  
  2. Lecture (GET by ID / GET ALL) :
     - Reconstitution transparente et performante de l'objet complet `HSEAuditOut`
       avec le dictionnaire `items_data` attendu par le frontend Vue 3.
  
  3. Cycle de vie et Nettoyage (DELETE) :
     - Suppression en cascade automatique de la soumission, de ses lignes d'évaluation
       et de ses enregistrements de photos.

Équipe de maintenance :
  - La normalisation des états d'action (`ETAT_NORMALIZE`) gère les variations
    avec ou sans accents ("non engagée" vs "non_engagee") pour éviter tout rejet.
  - La règle métier stricte sur les accidents de travail :
    `nb_accidents_total = nb_accidents_avec_arret + nb_accidents_sans_arret`.
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
    AccidentTravailSubmission,
    AccidentTravailMonthlyItem,
    CustomFieldDefinition,
    CustomFieldValue,
)
from app.schemas.audit import HSEAuditCreate, HSEAuditUpdate


# =============================================================================
# 1. DICTIONNAIRES DE MAPPAGE DES STATUTS D'ACTIONS CORRECTIVES
# =============================================================================
# Normalise les statuts reçus depuis le frontend vers les valeurs normalisées BDD
ETAT_NORMALIZE = {
    "non engagée": "non_engagee",
    "non engagee": "non_engagee",
    "en cours": "en_cours",
    "soldée": "soldee",
    "soldee": "soldee",
    "en retard": "en_retard",
}

# Convertit les codes BDD en libellés soignés avec accents pour l'affichage frontend
ETAT_DISPLAY = {
    "non_engagee": "Non engagée",
    "en_cours": "En cours",
    "soldee": "Soldée",
    "en_retard": "En retard",
}


# =============================================================================
# 2. SERVICE PRINCIPAL : SUBMISSIONSERVICE
# =============================================================================
class SubmissionService:
    """
    Service centralisant les opérations CRUD et la transformation relationnelle
    des formulaires de sécurité et santé au travail (HSE).
    """

    @staticmethod
    def _normalize_etat(etat_str: Optional[str]) -> str:
        """
        Convertit un libellé d'état d'action en valeur standardisée pour la BDD.
        Ex: 'Non engagée' -> 'non_engagee'.
        """
        if not etat_str:
            return "non_engagee"
        lower = etat_str.strip().lower()
        return ETAT_NORMALIZE.get(lower, "non_engagee")

    @staticmethod
    def _display_etat(etat_db: Optional[str]) -> str:
        """
        Convertit un code d'état BDD en libellé élégant pour le frontend.
        Ex: 'non_engagee' -> 'Non engagée'.
        """
        if not etat_db:
            return "Non engagée"
        return ETAT_DISPLAY.get(etat_db, etat_db)

    @classmethod
    def create_submission(cls, db: Session, audit_in: HSEAuditCreate, user_id: int) -> Dict[str, Any]:
        """
        Crée une nouvelle soumission et la ventile dans les tables relationnelles appropriées.

        Args:
            db (Session): Session de base de données active.
            audit_in (HSEAuditCreate): DTO validé contenant les données du formulaire.
            user_id (int): Identifiant du manager connecté.

        Returns:
            Dict[str, Any]: Dictionnaire complet reconstitué au format HSEAuditOut.
        """
        form_type = audit_in.form_type

        # Détermination du type de formulaire cible normalisé
        if form_type in ("audit_hse", "audit_hse_complet"):
            target_type = "audit_hse"
        elif form_type == "tournee_hse":
            target_type = "tournee_hse"
        elif form_type == "permis_travail":
            target_type = "permis_travail"
        elif form_type in ("statistiques_accidents", "accident_travail"):
            target_type = "statistiques_accidents"
        else:
            target_type = "audit_hse"

        # --- CAS 1 : FORMULAIRE D'AUDIT HSE COMPLET (FGSI-001) ---
        if target_type == "audit_hse":
            # Création de l'entité fille héritée de FormSubmission
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
            db.flush()  # Flush immédiat pour générer l'identifiant auto-incrémenté 'submission.id'

            # Éclatement des 51 questions dans la table relationnelle audit_hse_items
            cls._save_audit_items(db, submission.id, audit_in.items_data)

        # --- CAS 2 : FORMULAIRE DE TOURNÉE HSE (FGSI-010) ---
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

            # Enregistrement des points de contrôle dans tournee_hse_items
            cls._save_tournee_items(db, submission.id, audit_in.items_data)

        # --- CAS 3 : PERMIS DE TRAVAIL (FGSI-PERMIS) ---
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
                dynamic_fields=items_d.get("dynamic_fields") or None,
            )
            db.add(submission)
            db.flush()

            # Enregistrement relationnel dans la table custom_field_values
            if items_d.get("dynamic_fields"):
                cls._save_custom_field_values(db, submission.id, items_d.get("dynamic_fields"))

        # --- CAS 4 : SUIVI DES ACCIDENTS DE TRAVAIL ET STATISTIQUES HSE ---
        elif target_type == "statistiques_accidents":
            items_d = audit_in.items_data or {}
            # Extraction de l'année civile de référence
            annee_val = int(items_d.get("annee") or (audit_in.date_audit.split("-")[0] if "-" in audit_in.date_audit else 2026))
            submission = AccidentTravailSubmission(
                user_id=user_id,
                form_type=target_type,
                reference=audit_in.reference or "FGSI-STAT-ACCIDENTS",
                secteur=audit_in.secteur,
                intervenants=audit_in.intervenants,
                date_audit=audit_in.date_audit,
                taux_conformite=audit_in.taux_conformite or 100.0,
                commentaires_generaux=audit_in.commentaires_generaux,
                annee=annee_val,
                target_if=float(items_d.get("target_if") or 2.5),
                target_tf=float(items_d.get("target_tf") or 0.0),
                target_tg=float(items_d.get("target_tg") or 0.0),
                target_ig=float(items_d.get("target_ig") or 0.0),
            )
            db.add(submission)
            db.flush()

            # Enregistrement des 12 mois de statistiques
            cls._save_accident_travail_items(db, submission, items_d)

        # Validation de l'ensemble de la transaction
        db.commit()
        db.refresh(submission)

        # Reconstitution au format DTO complet
        return cls.submission_to_dict(submission)

    @classmethod
    def _save_accident_travail_items(cls, db: Session, submission: AccidentTravailSubmission, items_data: Dict[str, Any]):
        """
        Enregistre les 12 mois de statistiques accidents et calcule les totaux et indicateurs annuels.
        Règle métier stricte : nb_accidents_total = nb_accidents_avec_arret + nb_accidents_sans_arret.
        """
        months_dict = items_data.get("months", items_data)
        if not isinstance(months_dict, dict):
            months_dict = {}

        MOIS_LABELS = [
            "janv.", "févr.", "mars", "avr.", "mai", "juin",
            "juil.", "août", "sept.", "oct.", "nov.", "déc."
        ]
        annee_short = str(submission.annee)[-2:]

        # Cumulateurs pour consolidation annuelle
        tot_avec = 0
        tot_sans = 0
        tot_heures = 0.0
        tot_jours = 0
        tot_salaries = 0
        tot_visites = 0
        tot_maladies = 0

        # Itération sur les 12 mois de l'année
        for m_idx in range(1, 13):
            m_key = str(m_idx)
            m_data = months_dict.get(m_key, {})
            if not isinstance(m_data, dict):
                m_data = {}

            avec_arret = int(m_data.get("nb_accidents_avec_arret") or 0)
            sans_arret = int(m_data.get("nb_accidents_sans_arret") or 0)
            # Application de la règle métier de calcul de somme
            total_acc = avec_arret + sans_arret
            heures = float(m_data.get("nb_heures_travaillees") or 0.0)
            jours = int(m_data.get("nb_jours_perdus") or 0)
            salaries = int(m_data.get("nb_travailleurs") or m_data.get("nb_salaries") or 0)
            visites = int(m_data.get("nb_visites_medicales") or 0)
            maladies = int(m_data.get("nb_maladies_pro") or 0)
            incap_perm = float(m_data.get("incapacite_permanente") or m_data.get("somme_taux_incapacite_perm") or 0.0)

            # Formules réglementaires des indicateurs mensuels
            tf = round((avec_arret / heures) * 1_000_000, 2) if heures > 0 else 0.0
            inf = round((avec_arret / salaries) * 1_000, 2) if salaries > 0 else 0.0
            tg = round((jours * 1_000) / heures, 4) if heures > 0 else 0.0
            ig = round((incap_perm * 1_000) / heures, 4) if heures > 0 else 0.0

            # Création de la ligne mensuelle
            item = AccidentTravailMonthlyItem(
                submission_id=submission.id,
                mois_index=m_idx,
                mois_label=f"{MOIS_LABELS[m_idx - 1]}-{annee_short}",
                nb_accidents_total=total_acc,
                nb_accidents_avec_arret=avec_arret,
                nb_accidents_sans_arret=sans_arret,
                nb_heures_travaillees=heures,
                nb_jours_perdus=jours,
                nb_travailleurs=salaries,
                nb_visites_medicales=visites,
                nb_maladies_pro=maladies,
                tf_valeur=tf,
                if_valeur=inf,
                tg_valeur=tg,
                ig_valeur=ig,
                incapacite_permanente=incap_perm,
            )
            db.add(item)

            # Mise à jour des cumuls annuels
            tot_avec += avec_arret
            tot_sans += sans_arret
            tot_heures += heures
            tot_jours += jours
            tot_visites += visites
            tot_maladies += maladies
            if salaries > 0:
                tot_salaries = salaries

        # Affectation des totaux annuels consolidés à la soumission parente
        submission.total_accidents_avec_arret = tot_avec
        submission.total_accidents_sans_arret = tot_sans
        submission.total_accidents = tot_avec + tot_sans
        submission.total_heures_travaillees = tot_heures
        submission.total_jours_perdus = tot_jours
        submission.total_travailleurs = tot_salaries
        submission.total_visites_medicales = tot_visites
        submission.total_maladies_pro = tot_maladies

        # Calcul des indicateurs de synthèse annuels
        if tot_heures > 0:
            submission.taux_frequence = round((tot_avec / tot_heures) * 1_000_000, 2)
            submission.taux_gravite = round((tot_jours * 1_000) / tot_heures, 4)
        if tot_salaries > 0:
            submission.indice_frequence = round((tot_avec / tot_salaries) * 1_000, 2)

    @classmethod
    def _save_audit_items(cls, db: Session, audit_id: int, items_data: Dict[str, Any]):
        """
        Enregistre les questions détaillées de l'audit HSE dans la table `audit_hse_items`
        et référence les photographies dans `photo_storage`.
        """
        if not items_data or not isinstance(items_data, dict):
            return

        for q_key, val_data in items_data.items():
            try:
                q_id = int(q_key)
            except ValueError:
                continue

            if not isinstance(val_data, dict):
                val_data = {"val": val_data}

            # Normalisation de la conformité : 1 = Conforme, 0 = Non conforme, -1 = NA
            raw_val = val_data.get("val")
            if raw_val == "NA":
                conf = -1
            elif raw_val in (1, "1"):
                conf = 1
            else:
                conf = 0

            photo = val_data.get("photo")
            etat = cls._normalize_etat(val_data.get("etat"))

            # Création de la ligne relationnelle
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

            # Archivage de la preuve photo dans le registre centralisé si présente
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
        """
        Enregistre les points de contrôle de la Tournée HSE dans la table `tournee_hse_items`.
        """
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
    def _save_custom_field_values(cls, db: Session, submission_id: int, dynamic_fields: Any):
        """
        Enregistre les valeurs des champs personnalisés dans la table normalisée custom_field_values.
        Pour chaque champ personnalisé reçu :
          1. Retrouve ou crée la définition du champ dans le catalogue partagé (custom_field_definitions)
          2. Insère la valeur typée (numeric_value pour les calculs SQL / text_value pour le texte)
        """
        if not dynamic_fields or not isinstance(dynamic_fields, list):
            return

        # Supprimer les anciennes valeurs de cette soumission pour réécriture propre
        db.query(CustomFieldValue).filter(CustomFieldValue.submission_id == submission_id).delete()

        for f in dynamic_fields:
            if not isinstance(f, dict):
                continue

            label = str(f.get("label") or f.get("name") or "").strip()
            if not label:
                continue

            field_type = "numeric" if f.get("type") in ("numeric", "number") else "text"
            unit = str(f.get("unit") or "").strip()
            raw_val = f.get("value")

            # 1. Retrouver ou créer la définition dans le catalogue partagé
            field_def = db.query(CustomFieldDefinition).filter(
                CustomFieldDefinition.name == label,
                CustomFieldDefinition.form_type == "permis_travail"
            ).first()

            if not field_def:
                field_def = CustomFieldDefinition(
                    name=label,
                    field_type=field_type,
                    unit=unit,
                    form_type="permis_travail"
                )
                db.add(field_def)
                db.flush()

            # 2. Convertir la valeur selon le type
            num_val = None
            txt_val = None
            if field_type == "numeric":
                try:
                    num_val = float(raw_val) if raw_val is not None and str(raw_val).strip() != "" else 0.0
                except (ValueError, TypeError):
                    num_val = 0.0
            else:
                txt_val = str(raw_val) if raw_val is not None else ""

            # 3. Insérer la valeur relationnelle
            val_obj = CustomFieldValue(
                submission_id=submission_id,
                field_id=field_def.id,
                numeric_value=num_val,
                text_value=txt_val
            )
            db.add(val_obj)

    @classmethod
    def get_submission_by_id(cls, db: Session, audit_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Recherche une soumission par son identifiant et reconstitue son dictionnaire `items_data`.
        Toutes les fiches sont partagées et centralisées pour l'ensemble des utilisateurs de l'usine.

        Args:
            db (Session): Session BDD.
            audit_id (int): Identifiant unique de l'audit.
            user_id (Optional[int]): Optionnel (non restrictif pour permettre la vue partagée).

        Raises:
            HTTPException: Si l'audit est introuvable (erreur 404).

        Returns:
            Dict[str, Any]: Données complètes de la soumission.
        """
        sub = db.query(FormSubmission).filter(FormSubmission.id == audit_id).first()

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
        user_id: Optional[int] = None,
        date_audit: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        form_type: Optional[str] = None,
        secteur: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Récupère l'ensemble des soumissions centralisées de l'usine avec application
        de critères de filtrage optionnels (dates, type de formulaire, secteur).
        Toutes les fiches saisies par n'importe quel utilisateur sont visibles par tous.

        Returns:
            List[Dict[str, Any]]: Liste des soumissions prêtes pour le frontend.
        """
        # Requête de base sur la table mère polymorphique (données centralisées pour tous)
        query = db.query(FormSubmission)

        # Filtre optionnel si un utilisateur spécifique est expressément demandé
        if user_id is not None:
            query = query.filter(FormSubmission.user_id == user_id)

        # Filtre par date exacte
        if date_audit:
            query = query.filter(FormSubmission.date_audit == date_audit)
        # Filtres de plage temporelle (du ... au ...)
        if date_from:
            query = query.filter(FormSubmission.date_audit >= date_from)
        if date_to:
            query = query.filter(FormSubmission.date_audit <= date_to)
        # Filtre par catégorie de formulaire
        if form_type:
            if form_type in ("audit_hse", "audit_hse_complet"):
                query = query.filter(FormSubmission.form_type.in_(["audit_hse", "audit_hse_complet"]))
            else:
                query = query.filter(FormSubmission.form_type == form_type)
        # Recherche textuelle insensible à la casse sur le secteur ou les intervenants
        if secteur:
            query = query.filter(
                or_(
                    FormSubmission.secteur.ilike(f"%{secteur}%"),
                    FormSubmission.intervenants.ilike(f"%{secteur}%")
                )
            )

        # Tri antéchronologique (les plus récents en premier)
        submissions = query.order_by(FormSubmission.created_at.desc()).all()
        return [cls.submission_to_dict(s) for s in submissions]

    @classmethod
    def update_submission(
        cls, db: Session, audit_id: int, audit_in: HSEAuditUpdate, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Met à jour une soumission existante et synchronise en cascade ses points de contrôle.
        Accessible pour l'ensemble des fiches partagées de la plateforme.
        """
        sub = db.query(FormSubmission).filter(FormSubmission.id == audit_id).first()

        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit introuvable avec l'ID {audit_id}."
            )

        # Mise à jour des attributs communs déclarés dans form_submissions
        update_data = audit_in.model_dump(exclude_unset=True)
        for field in ("reference", "secteur", "intervenants", "date_audit", "commentaires_generaux", "taux_conformite"):
            if field in update_data and update_data[field] is not None:
                setattr(sub, field, update_data[field])

        # Mise à jour des compteurs statistiques sur les formulaires d'évaluation
        if isinstance(sub, (AuditHSESubmission, TourneeHSESubmission)):
            for field in ("total_conforme", "total_non_conforme", "total_na", "count_soldee", "count_non_engagee", "count_en_cours", "count_en_retard"):
                if field in update_data and update_data[field] is not None:
                    setattr(sub, field, update_data[field])

        # Synchronisation et recréation propre des items si le payload 'items_data' est fourni
        if "items_data" in update_data and update_data["items_data"] is not None:
            if isinstance(sub, AuditHSESubmission):
                # Suppression des anciens items avant réinsertion
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
                if "dynamic_fields" in items_d:
                    sub.dynamic_fields = items_d["dynamic_fields"]
                    cls._save_custom_field_values(db, sub.id, items_d["dynamic_fields"])
            elif isinstance(sub, AccidentTravailSubmission):
                items_d = update_data["items_data"]
                if "annee" in items_d:
                    sub.annee = int(items_d["annee"])
                if "target_if" in items_d:
                    sub.target_if = float(items_d["target_if"])
                if "target_tf" in items_d:
                    sub.target_tf = float(items_d["target_tf"])
                if "target_tg" in items_d:
                    sub.target_tg = float(items_d["target_tg"])
                if "target_ig" in items_d:
                    sub.target_ig = float(items_d["target_ig"])
                db.query(AccidentTravailMonthlyItem).filter(AccidentTravailMonthlyItem.submission_id == sub.id).delete()
                cls._save_accident_travail_items(db, sub, items_d)

        db.commit()
        db.refresh(sub)
        return cls.submission_to_dict(sub)

    @classmethod
    def delete_submission(cls, db: Session, audit_id: int, user_id: Optional[int] = None) -> bool:
        """
        Supprime définitivement une soumission.
        Grâce aux contraintes ON DELETE CASCADE, les tables filles et items
        sont automatiquement nettoyés par PostgreSQL.
        """
        sub = db.query(FormSubmission).filter(FormSubmission.id == audit_id).first()

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
        Reconstitue l'objet retourné exactement au format `HSEAuditOut` attendu
        par le frontend Vue 3, avec l'arborescence complète du dictionnaire `items_data`
        et le nom de l'auteur pour la vue partagée.
        """
        # Nom de l'auteur pour affichage clair dans l'historique partagé
        author_name = sub.user.full_name if (hasattr(sub, "user") and sub.user) else None

        # Base commune de toutes les soumissions
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
            "author_name": author_name,
            "created_at": sub.created_at,
        }

        # --- Reconstitution spécifique pour l'Audit HSE ---
        if isinstance(sub, AuditHSESubmission):
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

        # --- Reconstitution spécifique pour la Tournée HSE ---
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

        # --- Reconstitution pour le Permis de Travail ---
        elif isinstance(sub, PermisTravailSubmission):
            data["total_conforme"] = 0
            data["total_non_conforme"] = 0
            data["total_na"] = 0
            data["count_soldee"] = 0
            data["count_non_engagee"] = 0
            data["count_en_cours"] = 0
            data["count_en_retard"] = 0

            # Reconstitution depuis la table normalisée custom_field_values
            cf_list = []
            if hasattr(sub, "custom_field_values") and sub.custom_field_values:
                for cv in sub.custom_field_values:
                    fdef = cv.field_def
                    if fdef:
                        cf_list.append({
                            "fieldId": f"custom_{fdef.id}",
                            "label": fdef.name,
                            "type": fdef.field_type,
                            "value": cv.numeric_value if fdef.field_type == "numeric" else cv.text_value,
                            "unit": fdef.unit or "",
                            "isCustom": True,
                        })

            # Repli sur le JSON historique si aucune valeur relationnelle
            if not cf_list:
                cf_list = sub.dynamic_fields or []

            data["items_data"] = {
                "plan_prevention": sub.nb_plan_prevention,
                "permis_hauteur": sub.nb_permis_hauteur,
                "permis_feu": sub.nb_permis_feu,
                "remarques": sub.remarques_specifiques or "",
                "dynamic_fields": cf_list,
            }

        # --- Reconstitution pour le Bilan des Accidents de Travail ---
        elif isinstance(sub, AccidentTravailSubmission):
            data["total_conforme"] = 0
            data["total_non_conforme"] = 0
            data["total_na"] = 0
            data["count_soldee"] = 0
            data["count_non_engagee"] = 0
            data["count_en_cours"] = 0
            data["count_en_retard"] = 0

            months_dict = {}
            for it in (sub.monthly_items or []):
                months_dict[str(it.mois_index)] = {
                    "mois_index": it.mois_index,
                    "mois_label": it.mois_label,
                    "nb_accidents_total": it.nb_accidents_total,
                    "nb_accidents_avec_arret": it.nb_accidents_avec_arret,
                    "nb_accidents_sans_arret": it.nb_accidents_sans_arret,
                    "nb_heures_travaillees": it.nb_heures_travaillees,
                    "nb_jours_perdus": it.nb_jours_perdus,
                    "nb_travailleurs": it.nb_travailleurs,
                    "nb_visites_medicales": it.nb_visites_medicales,
                    "nb_maladies_pro": it.nb_maladies_pro,
                    "tf_valeur": it.tf_valeur,
                    "if_valeur": it.if_valeur,
                    "tg_valeur": it.tg_valeur,
                    "ig_valeur": it.ig_valeur,
                    "incapacite_permanente": it.incapacite_permanente,
                }

            data["items_data"] = {
                "annee": sub.annee,
                "target_if": sub.target_if,
                "target_tf": sub.target_tf,
                "target_tg": sub.target_tg,
                "target_ig": sub.target_ig,
                "totals": {
                    "total_accidents": sub.total_accidents,
                    "total_accidents_avec_arret": sub.total_accidents_avec_arret,
                    "total_accidents_sans_arret": sub.total_accidents_sans_arret,
                    "total_heures_travaillees": sub.total_heures_travaillees,
                    "total_jours_perdus": sub.total_jours_perdus,
                    "total_travailleurs": sub.total_travailleurs,
                    "total_visites_medicales": sub.total_visites_medicales,
                    "total_maladies_pro": sub.total_maladies_pro,
                    "taux_frequence": sub.taux_frequence,
                    "indice_frequence": sub.indice_frequence,
                    "taux_gravite": sub.taux_gravite,
                    "indice_gravite": sub.indice_gravite,
                },
                "months": months_dict,
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
