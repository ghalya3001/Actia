"""
===============================================================================
ENDPOINTS API — CHAMPS PERSONNALISÉS (CUSTOM_FIELDS.PY)
===============================================================================
Rôle :
  Gestion du catalogue de champs personnalisés (CustomFieldDefinition) :
  - GET  /custom-fields/definitions       : Liste tous les champs disponibles
  - POST /custom-fields/definitions       : Crée un nouveau champ personnalisé
  - GET  /custom-fields/values/{sub_id}   : Récupère les valeurs d'une soumission

Équipe de maintenance :
  Ces endpoints sont utilisés par le frontend (AuditWizard.vue) pour :
  1. Charger la liste des champs personnalisés dans le dropdown
  2. Enregistrer un nouveau champ dans le catalogue partagé
  3. Lire les valeurs enregistrées lors de l'édition d'un formulaire
===============================================================================
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.submission import CustomFieldDefinition, CustomFieldValue


router = APIRouter()


# =============================================================================
# SCHÉMAS PYDANTIC
# =============================================================================
class CustomFieldDefCreate(BaseModel):
    """Schéma de création d'une définition de champ personnalisé."""
    name: str = Field(..., min_length=1, max_length=255)
    field_type: str = Field(default="numeric", pattern="^(numeric|text)$")
    unit: Optional[str] = Field(default="")
    form_type: str = Field(default="permis_travail")


class CustomFieldDefOut(BaseModel):
    """Schéma de sortie d'une définition de champ personnalisé."""
    id: int
    name: str
    field_type: str
    unit: Optional[str] = ""
    form_type: str
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CustomFieldValueOut(BaseModel):
    """Schéma de sortie d'une valeur de champ personnalisé."""
    id: int
    submission_id: int
    field_id: int
    field_name: str
    field_type: str
    unit: Optional[str] = ""
    numeric_value: Optional[float] = None
    text_value: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# 1. LISTER LES DÉFINITIONS DE CHAMPS PERSONNALISÉS
# =============================================================================
@router.get(
    "/definitions",
    response_model=List[CustomFieldDefOut],
    summary="Liste le catalogue des champs personnalisés",
)
def list_custom_field_definitions(
    form_type: Optional[str] = Query(default=None, description="Filtrer par type de formulaire"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retourne toutes les définitions de champs personnalisés disponibles.
    Optionnellement filtrées par `form_type` (ex: 'permis_travail').
    """
    query = db.query(CustomFieldDefinition)
    if form_type:
        query = query.filter(CustomFieldDefinition.form_type == form_type)
    return query.order_by(CustomFieldDefinition.name).all()


# =============================================================================
# 2. CRÉER UNE NOUVELLE DÉFINITION DE CHAMP PERSONNALISÉ
# =============================================================================
@router.post(
    "/definitions",
    response_model=CustomFieldDefOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crée un nouveau champ personnalisé dans le catalogue",
)
def create_custom_field_definition(
    field_in: CustomFieldDefCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crée une nouvelle définition de champ personnalisé.
    Le champ sera visible par tous les utilisateurs dans le dropdown.
    """
    # Vérification de doublon (même nom + même form_type)
    existing = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.name == field_in.name.strip(),
        CustomFieldDefinition.form_type == field_in.form_type,
    ).first()

    if existing:
        # Retourner le champ existant plutôt que de créer un doublon
        return existing

    new_def = CustomFieldDefinition(
        name=field_in.name.strip(),
        field_type=field_in.field_type,
        unit=field_in.unit.strip() if field_in.unit else "",
        form_type=field_in.form_type,
        created_by=current_user.id,
    )
    db.add(new_def)
    db.commit()
    db.refresh(new_def)
    return new_def


# =============================================================================
# 3. RÉCUPÉRER LES VALEURS PERSONNALISÉES D'UNE SOUMISSION
# =============================================================================
@router.get(
    "/values/{submission_id}",
    response_model=List[CustomFieldValueOut],
    summary="Récupère les valeurs de champs personnalisés d'une soumission",
)
def get_custom_field_values(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retourne les valeurs des champs personnalisés associées à une soumission donnée.
    """
    values = (
        db.query(CustomFieldValue)
        .filter(CustomFieldValue.submission_id == submission_id)
        .all()
    )

    result = []
    for v in values:
        field_def = v.field_def
        result.append(CustomFieldValueOut(
            id=v.id,
            submission_id=v.submission_id,
            field_id=v.field_id,
            field_name=field_def.name if field_def else "Inconnu",
            field_type=field_def.field_type if field_def else "text",
            unit=field_def.unit if field_def else "",
            numeric_value=v.numeric_value,
            text_value=v.text_value,
        ))
    return result
