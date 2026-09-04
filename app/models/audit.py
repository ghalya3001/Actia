from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class HSEAudit(Base):
    __tablename__ = "hse_audits"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(100), default="FGSI-001-Ind:F", nullable=False)
    form_type = Column(String(100), default="audit_hse_complet", nullable=False)
    secteur = Column(String(255), nullable=False)
    intervenants = Column(String(255), nullable=False)
    date_audit = Column(String(100), nullable=False)
    commentaires_generaux = Column(Text, nullable=True)
    
    # Statistical KPI summaries
    taux_conformite = Column(Float, default=0.0, nullable=False)
    total_conforme = Column(Integer, default=0, nullable=False)
    total_non_conforme = Column(Integer, default=0, nullable=False)
    total_na = Column(Integer, default=0, nullable=False)
    
    count_soldee = Column(Integer, default=0, nullable=False)
    count_non_engagee = Column(Integer, default=0, nullable=False)
    count_en_cours = Column(Integer, default=0, nullable=False)
    count_en_retard = Column(Integer, default=0, nullable=False)

    # Structured Audit Data (Questions, Constats, Actions, Photos)
    items_data = Column(JSON, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", backref="audits")
