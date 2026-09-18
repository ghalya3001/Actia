"""
===============================================================================
MODÈLE DE DONNÉES HISTORIQUE — HSE_AUDITS (AUDIT.PY)
===============================================================================
Rôle :
  Représente la table `hse_audits` utilisée initialement pour persister
  les audits HSE au format JSON semi-structuré (`items_data`).

Équipe de maintenance :
  - Ce modèle est conservé pour assurer la rétrocompatibilité avec les premiers
    enregistrements créés lors du prototypage de la plateforme.
  - Pour les nouvelles fonctionnalités et analyses de données fines, l'application
    utilise préférentiellement les modèles normalisés de `app/models/submission.py`
    (Joined Table Inheritance).
===============================================================================
"""

from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class HSEAudit(Base):
    """
    Modèle d'audit HSE au format consolidé JSON.
    Stocke les métadonnées globales ainsi que la liste brute des questions/réponses en JSON.
    """
    __tablename__ = "hse_audits"

    # Clé primaire unique de l'audit
    id = Column(Integer, primary_key=True, index=True)

    # Référence documentaire officielle (ex: 'FGSI-001-Ind:F')
    reference = Column(String(100), default="FGSI-001-Ind:F", nullable=False)

    # Type de formulaire audité (ex: 'audit_hse_complet', 'tournee_hse')
    form_type = Column(String(100), default="audit_hse_complet", nullable=False)

    # Secteur ou zone géographique de l'usine auditée (ex: 'SMD-1', 'Magasin Central')
    secteur = Column(String(255), nullable=False)

    # Noms ou identités des auditeurs et personnes présentes
    intervenants = Column(String(255), nullable=False)

    # Date de réalisation de l'audit (format chaîne YYYY-MM-DD)
    date_audit = Column(String(100), nullable=False)

    # Commentaires et observations générales de l'auditeur
    commentaires_generaux = Column(Text, nullable=True)

    # --- Synthèse statistique des indicateurs de conformité ---
    # Pourcentage de conformité calculé : (conforme / (conforme + non_conforme)) * 100
    taux_conformite = Column(Float, default=0.0, nullable=False)

    # Nombre total de points évalués comme conformes
    total_conforme = Column(Integer, default=0, nullable=False)

    # Nombre total de points non conformes constatés
    total_non_conforme = Column(Integer, default=0, nullable=False)

    # Nombre total de points déclarés non applicables (N/A)
    total_na = Column(Integer, default=0, nullable=False)

    # --- Synthèse de suivi des plans d'action associés ---
    # Actions soldées (terminées et validées)
    count_soldee = Column(Integer, default=0, nullable=False)

    # Actions non engagées (en attente de démarrage)
    count_non_engagee = Column(Integer, default=0, nullable=False)

    # Actions en cours de réalisation
    count_en_cours = Column(Integer, default=0, nullable=False)

    # Actions en retard par rapport au délai prévu
    count_en_retard = Column(Integer, default=0, nullable=False)

    # --- Données structurées détaillées (Questions, Constats, Actions, Photos) ---
    # Contient l'arborescence JSON des questions évaluées avec leurs détails
    items_data = Column(JSON, nullable=False)

    # Clé étrangère vers l'utilisateur ayant créé l'audit
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Horodatage automatique de création dans la base
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relation ORM vers l'utilisateur auteur
    user = relationship("User", backref="audits")
