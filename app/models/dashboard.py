"""
===============================================================================
MODÈLES DE DONNÉES — DOMAINE DASHBOARD ET KPIS (DASHBOARD.PY)
===============================================================================
Rôle :
  Implémente l'architecture relationnelle dédiée au moteur de pilotage HSE :
  1. `KPIDefinition` : Catalogue déclaratif des indicateurs (formule, table source,
     type de restitution visuelle, regroupements).
  2. `KPISnapshot` : Cache haute performance contenant les résultats pré-calculés
     afin de restituer les graphiques et cartes en moins de 10 ms sans surcharge SQL.
  3. `DashboardWidget` : Configuration de l'agencement et de la grille visuelle
     personnalisée par utilisateur (position x, y, largeur, hauteur).

Équipe de maintenance :
  - Pour ajouter un nouveau KPI système sans toucher au code, insérez simplement une
    nouvelle ligne dans `kpi_definitions` avec `form_type`, `source_table`, `aggregation`.
  - Lors de chaque nouvelle soumission de formulaire, `KPIService.refresh_all_snapshots()`
    met à jour les enregistrements dans `kpi_snapshots`.
===============================================================================
"""

from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from app.db.base import Base


# =============================================================================
# 1. TABLE : KPI_DEFINITIONS (Catalogue des Indicateurs Configurables)
# =============================================================================
class KPIDefinition(Base):
    """
    Catalogue des indicateurs de performance (KPIs) disponibles sur la plateforme.
    Décrit la formule de calcul, la table SQL cible et le mode d'affichage graphique.
    """
    __tablename__ = "kpi_definitions"

    # Identifiant unique de la définition de KPI
    id = Column(Integer, primary_key=True, index=True)

    # Nom technique unique normalisé (ex: 'avg_conformite_audit', 'count_actions_retard')
    name = Column(String(100), unique=True, nullable=False, index=True)

    # Libellé lisible affiché dans l'interface (ex: 'Taux Moyen de Conformité')
    label = Column(String(255), nullable=False)

    # Description textuelle pédagogique de l'indicateur
    description = Column(Text, nullable=True)

    # Périmètre du formulaire cible ('audit_hse', 'tournee_hse', 'statistiques_accidents', ou 'all')
    form_type = Column(String(50), nullable=False, default="all")

    # Table SQL source sur laquelle s'applique le calcul ('audit_hse_items', 'form_submissions', etc.)
    source_table = Column(String(100), nullable=False)

    # Fonction d'agrégation SQL appliquée ('COUNT', 'AVG', 'SUM', 'PERCENT')
    aggregation = Column(String(50), nullable=False, default="COUNT")

    # Clause de filtre SQL optionnelle (ex: "etat = 'en_retard'", "conformite = 0")
    filter_condition = Column(String(500), nullable=True)

    # Colonne de regroupement SQL pour graphiques en barres ou camembert (ex: 'secteur', 'section_id')
    group_by_column = Column(String(100), nullable=True)

    # Type de composant graphique frontend associé ('card', 'doughnut', 'bar', 'line')
    chart_type = Column(String(50), nullable=False, default="card")

    # Indicateur d'activation du KPI dans le catalogue
    is_active = Column(Boolean, default=True, nullable=False)

    # Ordre de tri dans l'affichage du tableau de bord
    display_order = Column(Integer, default=0, nullable=False)

    # Date de création de la définition
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- Relations ORM ---
    # Instantanés de calculs générés pour ce KPI
    snapshots = relationship("KPISnapshot", back_populates="kpi_def", cascade="all, delete-orphan")

    # Widgets configurés dans les dashboards utilisateurs
    widgets = relationship("DashboardWidget", back_populates="kpi_def", cascade="all, delete-orphan")


# =============================================================================
# 2. TABLE : KPI_SNAPSHOTS (Résultats Pré-calculés en Cache)
# =============================================================================
class KPISnapshot(Base):
    """
    Résultats des indicateurs pré-calculés lors de la soumission de formulaires.
    Permet un affichage instantané du Dashboard (< 10ms) sans recalcul SQL lourd.
    """
    __tablename__ = "kpi_snapshots"

    # Identifiant unique de l'instantané
    id = Column(Integer, primary_key=True, index=True)

    # Clé étrangère vers la définition du KPI
    kpi_id = Column(Integer, ForeignKey("kpi_definitions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Utilisateur spécifique propriétaire de la vue (NULL si indicateur global usine)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Valeur numérique scalaire simple (utilisée pour les cartes de résumé KPI, ex: 87.5 %)
    value = Column(Float, nullable=True)

    # Données groupées au format JSON (pour alimenter directement Chart.js : labels, datasets)
    breakdown_data = Column(JSON, nullable=True)

    # Date de début de la fenêtre temporelle analysée (format ISO YYYY-MM-DD)
    period_start = Column(String(50), nullable=True)

    # Date de fin de la fenêtre temporelle analysée
    period_end = Column(String(50), nullable=True)

    # Horodatage précis du calcul de l'instantané
    computed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations ORM
    kpi_def = relationship("KPIDefinition", back_populates="snapshots")
    user = relationship("User", back_populates="kpi_snapshots")


# =============================================================================
# 3. TABLE : DASHBOARD_WIDGETS (Agencement Personnalisé par Utilisateur)
# =============================================================================
class DashboardWidget(Base):
    """
    Configuration de la disposition visuelle du Dashboard pour chaque manager.
    Définit les coordonnées (X, Y) et dimensions (Largeur, Hauteur) sur la grille.
    """
    __tablename__ = "dashboard_widgets"

    # Identifiant unique du widget
    id = Column(Integer, primary_key=True, index=True)

    # Utilisateur propriétaire de cette disposition
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Indicateur représenté par le widget
    kpi_id = Column(Integer, ForeignKey("kpi_definitions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Lien direct vers le snapshot en cache le plus récent
    kpi_snapshot_id = Column(Integer, ForeignKey("kpi_snapshots.id", ondelete="SET NULL"), nullable=True)

    # Position horizontale sur la grille (colonne 0, 1, 2...)
    position_x = Column(Integer, default=0, nullable=False)

    # Position verticale sur la grille (ligne 0, 1, 2...)
    position_y = Column(Integer, default=0, nullable=False)

    # Largeur en nombre de colonnes (ex: 1, 2, 3...)
    width = Column(Integer, default=1, nullable=False)

    # Hauteur en nombre de rangées
    height = Column(Integer, default=1, nullable=False)

    # Paramètres additionnels de personnalisation visuelle (couleurs, options Chart.js)
    extra_config = Column(JSON, nullable=True)

    # Horodatage de création du widget
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relations ORM
    user = relationship("User", back_populates="dashboard_widgets")
    kpi_def = relationship("KPIDefinition", back_populates="widgets")
    snapshot = relationship("KPISnapshot")
