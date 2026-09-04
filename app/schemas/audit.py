from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime

class HSEAuditCreate(BaseModel):
    reference: str = Field(default="FGSI-001-Ind:F")
    form_type: str = Field(default="audit_hse_complet")
    secteur: str
    intervenants: str
    date_audit: str
    commentaires_generaux: Optional[str] = None
    
    taux_conformite: float = 0.0
    total_conforme: int = 0
    total_non_conforme: int = 0
    total_na: int = 0
    
    count_soldee: int = 0
    count_non_engagee: int = 0
    count_en_cours: int = 0
    count_en_retard: int = 0

    items_data: Dict[str, Any]

class HSEAuditUpdate(BaseModel):
    reference: Optional[str] = None
    secteur: Optional[str] = None
    intervenants: Optional[str] = None
    date_audit: Optional[str] = None
    commentaires_generaux: Optional[str] = None
    
    taux_conformite: Optional[float] = None
    total_conforme: Optional[int] = None
    total_non_conforme: Optional[int] = None
    total_na: Optional[int] = None
    
    count_soldee: Optional[int] = None
    count_non_engagee: Optional[int] = None
    count_en_cours: Optional[int] = None
    count_en_retard: Optional[int] = None

    items_data: Optional[Dict[str, Any]] = None

class HSEAuditOut(BaseModel):
    id: int
    reference: str
    form_type: str
    secteur: str
    intervenants: str
    date_audit: str
    commentaires_generaux: Optional[str] = None
    
    taux_conformite: float
    total_conforme: int
    total_non_conforme: int
    total_na: int
    
    count_soldee: int
    count_non_engagee: int
    count_en_cours: int
    count_en_retard: int

    items_data: Dict[str, Any]
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class HSEAuditStats(BaseModel):
    total_audits: int
    avg_conformite: float
    total_actions_soldee: int
    total_actions_non_engagee: int
    total_actions_en_cours: int
    total_actions_en_retard: int
