from typing import List

from myst.models import base_model
from myst.openapi.models.hpo_job_get import HPOJobGet


class HPOJobGetList(base_model.BaseModel):
    """Schema for HPOJobGet list responses."""

    data: List[HPOJobGet]
    has_more: bool
