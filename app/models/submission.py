"""
===============================================================================
MODÈLES DE DONNÉES — DOMAINE FORMULAIRES HSE (SUBMISSION.PY)
===============================================================================
Ce module implémente l'architecture relationnelle des formulaires HSE selon
le patron Joined Table Inheritance (Héritage par Jointure) :
  - FormSubmission : Table mère stockant les métadonnées communes
  - AuditHSESubmission : Table fille spécialisée pour l'Audit HSE (FGSI-001)
  - AuditHSEItem : Table relationnelle des points de contrôle / actions Audit
  - TourneeHSESubmission : Table fille spécialisée pour la Tournée HSE (FGSI-010)
  - TourneeHSEItem : Table relationnelle des points de contrôle / actions Tournée
  - PermisTravailSubmission : Table fille pour les Permis de Travail (FGSI-PERMIS)
  - PhotoStorage : Registre centralisé des photos rattachées aux items
===============================================================================
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


# =============================================================================
# 1. TABLE MÈRE : FORM_SUBMISSIONS (Joined Table Inheritance)
# =============================================================================
class FormSubmission(Base):
    """
    Table mère commune à toutes les soumissions de formulaires HSE.
    Gère le polymorphisme via la colonne 'form_type'.
    """
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    form_type = Column(String(50), nullable=False, index=True)  # 'audit_hse', 'tournee_hse', 'permis_travail'
    reference = Column(String(100), nullable=False)            # 'FGSI-001-Ind:F', 'FGSI-010-Ind:A', 'FGSI-PERMIS'
    secteur = Column(String(255), nullable=False, index=True)
    intervenants = Column(String(255), nullable=False)
    date_audit = Column(String(50), nullable=False, index=True)  # Format YYYY-MM-DD
    taux_conformite = Column(Float, default=0.0, nullable=False)
    commentaires_generaux = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Configuration du polymorphisme SQLAlchemy
    __mapper_args__ = {
        "polymorphic_on": form_type,
        "polymorphic_identity": "form_submission",
    }

    # Relations
    user = relationship("User", back_populates="submissions")


# =============================================================================
# 2. TABLE FILLE : AUDIT_HSE_SUBMISSIONS (Audit HSE FGSI-001)
# =============================================================================
class AuditHSESubmission(FormSubmission):
    """
    Table enfant pour les fiches d'Audit HSE.
    Clé primaire partagée avec form_submissions.id.
    """
    __tablename__ = "audit_hse_submissions"

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

    __mapper_args__ = {
        "polymorphic_identity": "audit_hse",
    }

    # Relation 1 -> N vers les questions / items de l'audit
    items = relationship(
        "AuditHSEItem",
        back_populates="audit",
        cascade="all, delete-orphan",
        order_by="AuditHSEItem.question_id"
    )


# =============================================================================
# 3. TABLE ITEMS : AUDIT_HSE_ITEMS (Points de contrôle et actions)
# =============================================================================
class AuditHSEItem(Base):
    """
    Une ligne par question évaluée dans la grille d'Audit HSE (1 à 51).
    Contient le constat, le plan d'action et le statut de suivi.
    """
    __tablename__ = "audit_hse_items"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audit_hse_submissions.id", ondelete="CASCADE"), nullable=False, index=True)

    question_id = Column(Integer, nullable=False, index=True)
    section_id = Column(Integer, nullable=False, default=1)
    question_text = Column(Text, nullable=True)

    # Évaluation : 1 = Conforme, 0 = Non conforme, -1 = NA
    conformite = Column(Integer, default=1, nullable=False)

    # Détails en cas de non-conformité
    constat = Column(Text, nullable=True)
    photo_url = Column(Text, nullable=True)
    action_corrective = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=True)
    delai = Column(String(50), nullable=True)
    etat = Column(String(50), default="non_engagee", nullable=False)  # 'non_engagee', 'en_cours', 'soldee', 'en_retard'
    commentaire = Column(Text, nullable=True)

    # Relation vers l'audit parent
    audit = relationship("AuditHSESubmission", back_populates="items")


# =============================================================================
# 4. TABLE FILLE : TOURNEE_HSE_SUBMISSIONS (Tournée HSE FGSI-010)
# =============================================================================
class TourneeHSESubmission(FormSubmission):
    """
    Table enfant pour les Tournées HSE (FGSI-010-Ind:A).
    """
    __tablename__ = "tournee_hse_submissions"

    id = Column(Integer, ForeignKey("form_submissions.id", ondelete="CASCADE"), primary_key=True)

    total_conforme = Column(Integer, default=0, nullable=False)
    total_non_conforme = Column(Integer, default=0, nullable=False)
    total_na = Column(Integer, default=0, nullable=False)

    count_soldee = Column(Integer, default=0, nullable=False)
    count_non_engagee = Column(Integer, default=0, nullable=False)
    count_en_cours = Column(Integer, default=0, nullable=False)
    count_en_retard = Column(Integer, default=0, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "tournee_hse",
    }

    items = relationship(
        "TourneeHSEItem",
        back_populates="tournee",
        cascade="all, delete-orphan",
        order_by="TourneeHSEItem.question_id"
    )


# =============================================================================
# 5. TABLE ITEMS : TOURNEE_HSE_ITEMS
# =============================================================================
class TourneeHSEItem(Base):
    """
    Une ligne par question évaluée dans la Tournée HSE (101 à 142).
    """
    __tablename__ = "tournee_hse_items"

    id = Column(Integer, primary_key=True, index=True)
    tournee_id = Column(Integer, ForeignKey("tournee_hse_submissions.id", ondelete="CASCADE"), nullable=False, index=True)

    question_id = Column(Integer, nullable=False, index=True)
    section_id = Column(Integer, nullable=False, default=1)
    question_text = Column(Text, nullable=True)

    conformite = Column(Integer, default=1, nullable=False)

    constat = Column(Text, nullable=True)
    photo_url = Column(Text, nullable=True)
    action_corrective = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=True)
    delai = Column(String(50), nullable=True)
    etat = Column(String(50), default="non_engagee", nullable=False)
    commentaire = Column(Text, nullable=True)

    tournee = relationship("TourneeHSESubmission", back_populates="items")


# =============================================================================
# 6. TABLE FILLE : PERMIS_TRAVAIL_SUBMISSIONS (FGSI-PERMIS)
# =============================================================================
class PermisTravailSubmission(FormSubmission):
    """
    Table enfant pour les Permis de Travail (plans de prévention, travail en hauteur, permis de feu).
    """
    __tablename__ = "permis_travail_submissions"

    id = Column(Integer, ForeignKey("form_submissions.id", ondelete="CASCADE"), primary_key=True)

    nb_plan_prevention = Column(Integer, default=0, nullable=False)
    nb_permis_hauteur = Column(Integer, default=0, nullable=False)
    nb_permis_feu = Column(Integer, default=0, nullable=False)
    remarques_specifiques = Column(Text, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "permis_travail",
    }


# =============================================================================
# 7. TABLE : PHOTO_STORAGE (Registre centralisé des photos)
# =============================================================================
class PhotoStorage(Base):
    """
    Registre des photos prises lors des évaluations terrain.
    """
    __tablename__ = "photo_storage"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, nullable=False, index=True)
    item_type = Column(String(50), nullable=False, default="audit_hse")  # 'audit_hse' ou 'tournee_hse'
    file_path = Column(Text, nullable=False)
    original_filename = Column(String(255), nullable=True)
    file_size_kb = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
