from typing import List

from myst.models import base_model
from myst.openapi.models.project_get import ProjectGet


class ProjectList(base_model.BaseModel):
    """Schema for project list responses."""

    data: List[ProjectGet]
    has_more: bool
