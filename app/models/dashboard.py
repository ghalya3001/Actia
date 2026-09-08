"""
===============================================================================
MODÈLES DE DONNÉES — DOMAINE DASHBOARD & KPIS (DASHBOARD.PY)
===============================================================================
Ce module implémente les 3 tables dédiées au pilotage du Dashboard dynamique :
  - KPIDefinition : Catalogue des indicateurs configurables
  - KPISnapshot : Résultats calculés (cache haute performance)
  - DashboardWidget : Configuration de l'agencement utilisateur
===============================================================================
"""

from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from app.db.base import Base


# =============================================================================
# 1. TABLE : KPI_DEFINITIONS (Catalogue des indicateurs)
# =============================================================================
class KPIDefinition(Base):
    """
    Catalogue des KPIs disponibles sur la plateforme.
    Décrit la formule, la table source, et le type de graphique associé.
    """
    __tablename__ = "kpi_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)   # Ex: 'avg_conformite_audit'
    label = Column(String(255), nullable=False)                         # Ex: 'Taux Moyen de Conformité'
    description = Column(Text, nullable=True)
    form_type = Column(String(50), nullable=False, default="all")       # 'audit_hse', 'tournee_hse', 'all'
    source_table = Column(String(100), nullable=False)                  # 'audit_hse_items', 'form_submissions'
    aggregation = Column(String(50), nullable=False, default="COUNT")   # 'COUNT', 'AVG', 'SUM'
    filter_condition = Column(String(500), nullable=True)               # Ex: "etat = 'en_retard'"
    group_by_column = Column(String(100), nullable=True)                # Ex: 'secteur', 'section_id'
    chart_type = Column(String(50), nullable=False, default="card")     # 'card', 'doughnut', 'bar', 'line'
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relations
    snapshots = relationship("KPISnapshot", back_populates="kpi_def", cascade="all, delete-orphan")
    widgets = relationship("DashboardWidget", back_populates="kpi_def", cascade="all, delete-orphan")


# =============================================================================
# 2. TABLE : KPI_SNAPSHOTS (Résultats pré-calculés en cache)
# =============================================================================
class KPISnapshot(Base):
    """
    Résultats pré-calculés lors de la soumission de formulaires.
    Permet un affichage instantané du Dashboard (< 10ms) sans recalcul SQL lourd.
    """
    __tablename__ = "kpi_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    kpi_id = Column(Integer, ForeignKey("kpi_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # NULL si global

    value = Column(Float, nullable=True)          # Valeur numérique simple (pour cartes KPI)
    breakdown_data = Column(JSON, nullable=True)  # Données complexes groupées (pour graphiques camembert/bar/line)
    period_start = Column(String(50), nullable=True)
    period_end = Column(String(50), nullable=True)

    computed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    kpi_def = relationship("KPIDefinition", back_populates="snapshots")
    user = relationship("User", back_populates="kpi_snapshots")


# =============================================================================
# 3. TABLE : DASHBOARD_WIDGETS (Agencement personnalisé par utilisateur)
# =============================================================================
class DashboardWidget(Base):
    """
    Configuration de la grille du Dashboard pour chaque utilisateur.
    Définit quels widgets sont affichés, leur position et dimension.
    """
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kpi_id = Column(Integer, ForeignKey("kpi_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    kpi_snapshot_id = Column(Integer, ForeignKey("kpi_snapshots.id", ondelete="SET NULL"), nullable=True)

    position_x = Column(Integer, default=0, nullable=False)
    position_y = Column(Integer, default=0, nullable=False)
    width = Column(Integer, default=1, nullable=False)
    height = Column(Integer, default=1, nullable=False)
    extra_config = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relations
    user = relationship("User", back_populates="dashboard_widgets")
    kpi_def = relationship("KPIDefinition", back_populates="widgets")
    snapshot = relationship("KPISnapshot")
