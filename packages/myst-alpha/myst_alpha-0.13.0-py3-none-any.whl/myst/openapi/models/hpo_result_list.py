from typing import List

from myst.models import base_model
from myst.openapi.models.hpo_result_get import HPOResultGet


class HPOResultList(base_model.BaseModel):
    """Schema for model fit result list responses."""

    data: List[HPOResultGet]
    has_more: bool
