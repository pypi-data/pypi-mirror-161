from typing import List

from myst.models import base_model
from myst.openapi.models.deployment_get import DeploymentGet


class DeploymentList(base_model.BaseModel):
    """Schema for deployment list responses."""

    data: List[DeploymentGet]
    has_more: bool
