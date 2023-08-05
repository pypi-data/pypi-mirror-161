from typing import List

from myst.models import base_model
from myst.openapi.models.hpo_get import HPOGet


class HPOGetList(base_model.BaseModel):
    """Schema for HPOGet list responses."""

    data: List[HPOGet]
    has_more: bool
