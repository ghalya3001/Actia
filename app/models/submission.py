"""
===============================================================================
MODÈLES DE DONNÉES — DOMAINE FORMULAIRES ET SOUMISSIONS HSE (SUBMISSION.PY)
===============================================================================
Rôle :
  Implémente l'architecture relationnelle normalisée pour l'ensemble des formulaires
  terrain HSE selon le patron de conception "Joined Table Inheritance" (Héritage par Jointure) :
  
  1. `FormSubmission` : Table mère polymorphique contenant les métadonnées partagées
     (identifiant, auteur, secteur, date, référence, taux de conformité, etc.).
  2. Tables filles spécialisées :
     - `AuditHSESubmission` : Fiche d'audit complet (51 points de contrôle - FGSI-001).
     - `TourneeHSESubmission` : Grille de tournée de sécurité terrain (FGSI-010).
     - `PermisTravailSubmission` : Autorisations de travaux à risques (FGSI-PERMIS).
     - `AccidentTravailSubmission` : Suivi annuel et mensuel de la sinistralité HSE.
  3. Tables d'éléments de contrôle détaillés (1 formulaire vers N questions) :
     - `AuditHSEItem` : Détails d'évaluation par question (constat, action, responsable, délai, état).
     - `TourneeHSEItem` : Points de contrôle spécifiques à la tournée terrain.
     - `AccidentTravailMonthlyItem` : Données mensuelles détaillées (janvier à décembre).
  4. Registre photographique centralisé :
     - `PhotoStorage` : Gestion des clichés de preuves terrain rattachés aux non-conformités.

Équipe de maintenance :
  - Le polymorphisme SQLAlchemy repose sur la colonne `form_type` de `form_submissions`.
  - Quand vous requêtez `db.query(FormSubmission)`, SQLAlchemy effectue automatiquement
    les jointures appropriées (LEFT OUTER JOIN) vers les tables filles selon `polymorphic_identity`.
===============================================================================
"""

import enum

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.db.base import Base


# =============================================================================
# ENUMS : CONFORMITÉ & ÉTAT DES ACTIONS CORRECTIVES
# =============================================================================
class Conformite(int, enum.Enum):
    """Résultat d'évaluation d'un point de contrôle terrain."""
    CONFORME = 1          # Le point est conforme aux exigences
    NON_CONFORME = 0      # Non-conformité détectée
    NON_APPLICABLE = -1   # Critère non applicable au contexte du secteur


class EtatAction(str, enum.Enum):
    """Cycle de vie d'une action corrective issue d'une non-conformité."""
    NON_ENGAGEE = "non_engagee"   # Action en attente de démarrage
    EN_COURS = "en_cours"         # Action en cours de réalisation
    SOLDEE = "soldee"             # Action clôturée avec succès
    EN_RETARD = "en_retard"       # Délai dépassé, action non terminée


# =============================================================================
# 1. TABLE MÈRE : FORM_SUBMISSIONS (Joined Table Inheritance)
# =============================================================================
class FormSubmission(Base):
    """
    Table mère commune à toutes les soumissions de formulaires HSE.
    Elle centralise l'identité, l'auteur, la date et le secteur géographique.
    """
    __tablename__ = "form_submissions"

    # Identifiant unique universel de la soumission (clé primaire partagée avec les tables filles)
    id = Column(Integer, primary_key=True, index=True)

    # Identifiant du manager ayant soumis le formulaire (clé étrangère vers 'users.id')
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Type discriminant du formulaire ('audit_hse', 'tournee_hse', 'permis_travail', 'statistiques_accidents')
    form_type = Column(String(50), nullable=False, index=True)

    # Référence documentaire qualité usine (ex: 'FGSI-001-Ind:F', 'FGSI-010-Ind:A', 'FGSI-PERMIS')
    reference = Column(String(100), nullable=False)

    # Secteur ou atelier de l'usine concerné (ex: 'CMS / SMD', 'Magasin Central', 'Zone Vernissage')
    secteur = Column(String(255), nullable=False, index=True)

    # Noms des intervenants, auditeurs et accompagnateurs lors du contrôle
    intervenants = Column(String(255), nullable=False)

    # Date de réalisation du contrôle (format ISO YYYY-MM-DD)
    date_audit = Column(String(50), nullable=False, index=True)

    # Taux global de conformité calculé en pourcentage (0.0 à 100.0 %)
    taux_conformite = Column(Float, default=0.0, nullable=False)

    # Commentaires, synthèse ou remarques générales rédigées par l'auditeur
    commentaires_generaux = Column(Text, nullable=True)

    # Horodatage automatique de la création de la fiche
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Horodatage de la dernière modification (mise à jour automatique)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Configuration du polymorphisme SQLAlchemy pour l'héritage par jointure
    __mapper_args__ = {
        "polymorphic_on": form_type,
        "polymorphic_identity": "form_submission",
    }

    # Relation vers l'utilisateur auteur de la fiche
    user = relationship("User", back_populates="submissions")

    # Valeurs de champs personnalisés associées à cette soumission
    custom_field_values = relationship("CustomFieldValue", back_populates="submission", cascade="all, delete-orphan")


# =============================================================================
# 2. TABLE FILLE : AUDIT_HSE_SUBMISSIONS (Audit HSE Complet FGSI-001)
# =============================================================================
class AuditHSESubmission(FormSubmission):
    """
    Table enfant pour les fiches d'Audit HSE complet (51 questions réparties en 7 sections).
    Hérite de 'form_submissions' et partage sa clé primaire 'id'.
    """
    __tablename__ = "audit_hse_submissions"

    # Clé primaire liée en CASCADE à la table mère form_submissions
    id = Column(Integer, ForeignKey("form_submissions.id", ondelete="CASCADE"), primary_key=True)

    # Compteurs statistiques de l'évaluation terrain
    total_conforme = Column(Integer, default=0, nullable=False)        # Total des points conformes (valeur 1)
    total_non_conforme = Column(Integer, default=0, nullable=False)    # Total des non-conformités (valeur 0)
    total_na = Column(Integer, default=0, nullable=False)              # Total des critères non applicables (-1)

    # Compteurs de suivi des plans d'action issus de l'audit
    count_soldee = Column(Integer, default=0, nullable=False)          # Actions soldées / clôturées
    count_non_engagee = Column(Integer, default=0, nullable=False)     # Actions non engagées (en attente)
    count_en_cours = Column(Integer, default=0, nullable=False)        # Actions en cours de réalisation
    count_en_retard = Column(Integer, default=0, nullable=False)       # Actions dont le délai est dépassé

    # Déclaration de l'identité polymorphique pour l'audit HSE
    __mapper_args__ = {
        "polymorphic_identity": "audit_hse",
    }

    # Relation 1 -> N vers les 51 points de contrôle détaillés (triés par question_id)
    items = relationship(
        "AuditHSEItem",
        back_populates="audit",
        cascade="all, delete-orphan",
        order_by="AuditHSEItem.question_id"
    )


# =============================================================================
# 3. TABLE DES ITEMS D'AUDIT : AUDIT_HSE_ITEMS (Points de contrôle et actions)
# =============================================================================
class AuditHSEItem(Base):
    """
    Une ligne par question évaluée dans la grille d'Audit HSE (questions 1 à 51).
    Enregistre le constat terrain, la photo éventuelle et le plan d'action correctif.
    """
    __tablename__ = "audit_hse_items"

    # Identifiant unique de la ligne de contrôle
    id = Column(Integer, primary_key=True, index=True)

    # Clé étrangère vers l'audit parent
    audit_id = Column(Integer, ForeignKey("audit_hse_submissions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Numéro d'ordre de la question dans le référentiel officiel (1 à 51)
    question_id = Column(Integer, nullable=False, index=True)

    # Identifiant de la section thématique (1: EPI, 2: 5S, 3: Machines, etc.)
    section_id = Column(Integer, nullable=False, default=1)

    # Libellé textuel de la question au moment de l'audit
    question_text = Column(Text, nullable=True)

    # Évaluation : CONFORME(1), NON_CONFORME(0), NON_APPLICABLE(-1)
    conformite = Column(Integer, default=Conformite.CONFORME.value, nullable=False)

    # --- Champs spécifiques en cas de non-conformité ---
    constat = Column(Text, nullable=True)             # Description détaillée de l'anomalie observée
    photo_url = Column(Text, nullable=True)           # Chemin ou base64 de la photo de preuve
    action_corrective = Column(Text, nullable=True)   # Mesure corrective décidée pour traiter l'anomalie
    responsable = Column(String(255), nullable=True)  # Porteur de l'action corrective
    delai = Column(String(50), nullable=True)         # Date limite d'exécution prévue
    etat = Column(String(50), default=EtatAction.NON_ENGAGEE.value, nullable=False)  # Enum: NON_ENGAGEE, EN_COURS, SOLDEE, EN_RETARD
    commentaire = Column(Text, nullable=True)         # Note ou observation complémentaire

    # Relation inverse vers la fiche d'audit parente
    audit = relationship("AuditHSESubmission", back_populates="items")


# =============================================================================
# 4. TABLE FILLE : TOURNEE_HSE_SUBMISSIONS (Tournée de Sécurité FGSI-010)
# =============================================================================
class TourneeHSESubmission(FormSubmission):
    """
    Table enfant pour les fiches de Tournée HSE terrain (42 points de contrôle - FGSI-010-Ind:A).
    """
    __tablename__ = "tournee_hse_submissions"

    # Clé primaire partagée avec form_submissions
    id = Column(Integer, ForeignKey("form_submissions.id", ondelete="CASCADE"), primary_key=True)

    # Compteurs statistiques de conformité
    total_conforme = Column(Integer, default=0, nullable=False)
    total_non_conforme = Column(Integer, default=0, nullable=False)
    total_na = Column(Integer, default=0, nullable=False)

    # Compteurs statistiques des plans d'action
    count_soldee = Column(Integer, default=0, nullable=False)
    count_non_engagee = Column(Integer, default=0, nullable=False)
    count_en_cours = Column(Integer, default=0, nullable=False)
    count_en_retard = Column(Integer, default=0, nullable=False)

    # Déclaration de l'identité polymorphique pour la tournée
    __mapper_args__ = {
        "polymorphic_identity": "tournee_hse",
    }

    # Relation 1 -> N vers les questions de la tournée
    items = relationship(
        "TourneeHSEItem",
        back_populates="tournee",
        cascade="all, delete-orphan",
        order_by="TourneeHSEItem.question_id"
    )


# =============================================================================
# 5. TABLE DES ITEMS DE TOURNÉE : TOURNEE_HSE_ITEMS
# =============================================================================
class TourneeHSEItem(Base):
    """
    Une ligne par question évaluée lors de la Tournée HSE (questions 101 à 142).
    """
    __tablename__ = "tournee_hse_items"

    id = Column(Integer, primary_key=True, index=True)
    tournee_id = Column(Integer, ForeignKey("tournee_hse_submissions.id", ondelete="CASCADE"), nullable=False, index=True)

    question_id = Column(Integer, nullable=False, index=True)
    section_id = Column(Integer, nullable=False, default=1)
    question_text = Column(Text, nullable=True)

    # Évaluation : CONFORME(1), NON_CONFORME(0), NON_APPLICABLE(-1)
    conformite = Column(Integer, default=Conformite.CONFORME.value, nullable=False)

    constat = Column(Text, nullable=True)
    photo_url = Column(Text, nullable=True)
    action_corrective = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=True)
    delai = Column(String(50), nullable=True)
    etat = Column(String(50), default=EtatAction.NON_ENGAGEE.value, nullable=False)  # Enum: NON_ENGAGEE, EN_COURS, SOLDEE, EN_RETARD
    commentaire = Column(Text, nullable=True)

    tournee = relationship("TourneeHSESubmission", back_populates="items")


# =============================================================================
# 6. TABLE FILLE : PERMIS_TRAVAIL_SUBMISSIONS (Permis de Travail FGSI-PERMIS)
# =============================================================================
class PermisTravailSubmission(FormSubmission):
    """
    Table enfant pour le suivi des autorisations et permis de travail à risques
    (Plans de prévention, Permis de travail en hauteur, Permis de feu).
    """
    __tablename__ = "permis_travail_submissions"

    id = Column(Integer, ForeignKey("form_submissions.id", ondelete="CASCADE"), primary_key=True)

    # Nombre de plans de prévention rédigés et validés
    nb_plan_prevention = Column(Integer, default=0, nullable=False)

    # Nombre d'autorisations pour travaux en hauteur délivrées
    nb_permis_hauteur = Column(Integer, default=0, nullable=False)

    # Nombre de permis de feu délivrés (travaux avec point chaud, soudure, meulage)
    nb_permis_feu = Column(Integer, default=0, nullable=False)

    # Remarques particulières et mesures de sécurité spécifiques prescrites
    remarques_specifiques = Column(Text, nullable=True)

    # Champs dynamiques personnalisés et standards configurés (liste JSON)
    dynamic_fields = Column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "permis_travail",
    }


# =============================================================================
# 7. TABLE : PHOTO_STORAGE (Registre centralisé des photographies terrain)
# =============================================================================
class PhotoStorage(Base):
    """
    Table d'archivage des photos prises lors des évaluations terrain.
    Assure le lien entre un fichier image physique et la question évaluée.
    """
    __tablename__ = "photo_storage"

    id = Column(Integer, primary_key=True, index=True)

    # Identifiant de la question évaluée (item_id)
    item_id = Column(Integer, nullable=False, index=True)

    # Domaine d'appartenance de la photo ('audit_hse' ou 'tournee_hse')
    item_type = Column(String(50), nullable=False, default="audit_hse")

    # Chemin relatif sur disque ou chaîne d'accès au fichier image
    file_path = Column(Text, nullable=False)

    # Nom de fichier d'origine envoyé par le navigateur / mobile
    original_filename = Column(String(255), nullable=True)

    # Taille du fichier en kilo-octets (Ko)
    file_size_kb = Column(Integer, nullable=True)

    # Horodatage du téléversement
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# =============================================================================
# 8. TABLE FILLE : ACCIDENT_TRAVAIL_SUBMISSIONS (Bilan Annuel Sinistralité HSE)
# =============================================================================
class AccidentTravailSubmission(FormSubmission):
    """
    Table enfant pour le suivi annuel des statistiques d'accidents de travail
    et des indicateurs réglementaires de santé et sécurité au travail.
    """
    __tablename__ = "accident_travail_submissions"

    id = Column(Integer, ForeignKey("form_submissions.id", ondelete="CASCADE"), primary_key=True)

    # Année civile de référence (ex: 2026)
    annee = Column(Integer, default=2026, nullable=False)

    # --- Totaux annuels consolidés sur l'ensemble des 12 mois ---
    total_accidents = Column(Integer, default=0, nullable=False)
    total_accidents_avec_arret = Column(Integer, default=0, nullable=False)
    total_accidents_sans_arret = Column(Integer, default=0, nullable=False)
    total_heures_travaillees = Column(Float, default=0.0, nullable=False)
    total_jours_perdus = Column(Integer, default=0, nullable=False)
    total_travailleurs = Column(Integer, default=0, nullable=False)
    total_visites_medicales = Column(Integer, default=0, nullable=False)
    total_maladies_pro = Column(Integer, default=0, nullable=False)

    # --- Indicateurs annuels normalisés de référence ---
    # Taux de Fréquence : TF = (Accidents avec arrêt / Heures travaillées) * 1 000 000
    taux_frequence = Column(Float, default=0.0, nullable=False)

    # Indice de Fréquence : IF = (Accidents avec arrêt / Nombre de salariés) * 1 000
    indice_frequence = Column(Float, default=0.0, nullable=False)

    # Taux de Gravité : TG = (Jours perdus * 1 000) / Heures travaillées
    taux_gravite = Column(Float, default=0.0, nullable=False)

    # Indice de Gravité : IG = (Somme des taux d'incapacité permanente * 1 000) / Heures travaillées
    indice_gravite = Column(Float, default=0.0, nullable=False)

    # Objectifs et cibles définis par la direction HSE pour l'année
    target_if = Column(Float, default=2.5, nullable=False)  # Cible Indice Fréquence (ex: < 2.5)
    target_tf = Column(Float, default=0.0, nullable=False)  # Cible Taux Fréquence
    target_tg = Column(Float, default=0.0, nullable=False)  # Cible Taux Gravité
    target_ig = Column(Float, default=0.0, nullable=False)  # Cible Indice Gravité

    __mapper_args__ = {
        "polymorphic_identity": "statistiques_accidents",
    }

    # Relation 1 -> 12 vers les lignes de données mensuelles (janvier à décembre)
    monthly_items = relationship(
        "AccidentTravailMonthlyItem",
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="AccidentTravailMonthlyItem.mois_index"
    )


# =============================================================================
# 9. TABLE : ACCIDENT_TRAVAIL_MONTHLY_ITEMS (Détail des 12 Mois de l'Année)
# =============================================================================
class AccidentTravailMonthlyItem(Base):
    """
    Enregistrement par mois (de 1 = janvier à 12 = décembre) stockant
    les données brutes et les indicateurs calculés pour le mois.
    """
    __tablename__ = "accident_travail_monthly_items"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("accident_travail_submissions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Numéro du mois (1 à 12)
    mois_index = Column(Integer, nullable=False)

    # Libellé du mois (ex: 'janv.-26', 'févr.-26', 'mars-26')
    mois_label = Column(String(50), nullable=False)

    # 1. Total d'accidents du mois (Ligne 1 = Ligne 2 + Ligne 3)
    nb_accidents_total = Column(Integer, default=0, nullable=False)

    # 2. Nombre d'accidents ayant entraîné un arrêt de travail
    nb_accidents_avec_arret = Column(Integer, default=0, nullable=False)

    # 3. Nombre d'accidents de travail bénins sans arrêt
    nb_accidents_sans_arret = Column(Integer, default=0, nullable=False)

    # 4. Volume total des heures travaillées par le personnel dans le mois
    nb_heures_travaillees = Column(Float, default=0.0, nullable=False)

    # 5. Nombre cumulé de jours de travail perdus consécutifs aux arrêts
    nb_jours_perdus = Column(Integer, default=0, nullable=False)

    # 6. Effectif moyen des salariés / travailleurs présents
    nb_travailleurs = Column(Integer, default=0, nullable=False)

    # 7. Nombre de visites médicales obligatoires ou spontanées effectuées
    nb_visites_medicales = Column(Integer, default=0, nullable=False)

    # 8. Nombre de maladies professionnelles déclarées / reconnues
    nb_maladies_pro = Column(Integer, default=0, nullable=False)

    # --- Indicateurs mensuels calculés ---
    tf_valeur = Column(Float, default=0.0, nullable=False)               # Taux de Fréquence mensuel
    if_valeur = Column(Float, default=0.0, nullable=False)               # Indice de Fréquence mensuel
    tg_valeur = Column(Float, default=0.0, nullable=False)               # Taux de Gravité mensuel
    ig_valeur = Column(Float, default=0.0, nullable=False)               # Indice de Gravité mensuel
    incapacite_permanente = Column(Float, default=0.0, nullable=False)   # Somme des taux d'incapacité permanente

    # Relation inverse vers la soumission annuelle parente
    submission = relationship("AccidentTravailSubmission", back_populates="monthly_items")


# =============================================================================
# 10. TABLE : CUSTOM_FIELD_DEFINITIONS (Catalogue des Champs Personnalisés)
# =============================================================================
class CustomFieldDefinition(Base):
    """
    Catalogue partagé des champs personnalisés créés par les managers.
    Chaque définition est réutilisable par tous les utilisateurs : quand un manager
    crée le champ « Extincteurs vérifiés », tous les autres le voient dans leur dropdown.
    """
    __tablename__ = "custom_field_definitions"

    # Identifiant unique du champ personnalisé
    id = Column(Integer, primary_key=True, index=True)

    # Nom lisible du champ (ex: 'Extincteurs vérifiés', 'Nom du sous-traitant')
    name = Column(String(255), nullable=False)

    # Type de données : 'numeric' (chiffres, calculs) ou 'text' (texte libre)
    field_type = Column(String(50), nullable=False, default="numeric")

    # Unité de mesure ou descripteur (ex: 'Unités', 'Permis délivrés', 'Texte')
    unit = Column(String(100), nullable=True, default="")

    # Type de formulaire auquel ce champ est rattaché ('permis_travail', 'audit_hse', 'all')
    form_type = Column(String(50), nullable=False, default="permis_travail", index=True)

    # Identifiant du manager ayant créé ce champ (NULL si champ système)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Horodatage de création
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- Relations ORM ---
    # Toutes les valeurs saisies pour ce champ à travers les soumissions
    values = relationship("CustomFieldValue", back_populates="field_def", cascade="all, delete-orphan")

    # Utilisateur créateur
    creator = relationship("User", foreign_keys=[created_by])


# =============================================================================
# 11. TABLE : CUSTOM_FIELD_VALUES (Valeurs par Soumission)
# =============================================================================
class CustomFieldValue(Base):
    """
    Stocke la valeur d'un champ personnalisé pour une soumission donnée.
    Sépare numeric_value et text_value pour permettre les agrégations SQL
    (AVG, SUM, COUNT) sur les champs numériques depuis le Dashboard.
    """
    __tablename__ = "custom_field_values"

    # Identifiant unique de la valeur
    id = Column(Integer, primary_key=True, index=True)

    # Soumission parente (pointe vers form_submissions pour supporter TOUS les types)
    submission_id = Column(Integer, ForeignKey("form_submissions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Définition du champ personnalisé associé
    field_id = Column(Integer, ForeignKey("custom_field_definitions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Valeur numérique (utilisée quand field_type = 'numeric') — permet AVG, SUM, GROUP BY en SQL
    numeric_value = Column(Float, nullable=True)

    # Valeur textuelle (utilisée quand field_type = 'text')
    text_value = Column(Text, nullable=True)

    # Horodatage de création
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- Relations ORM ---
    field_def = relationship("CustomFieldDefinition", back_populates="values")
    submission = relationship("FormSubmission", back_populates="custom_field_values")

