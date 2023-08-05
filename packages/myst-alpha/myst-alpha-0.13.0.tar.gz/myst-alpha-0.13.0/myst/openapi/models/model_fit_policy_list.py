from typing import List

from myst.models import base_model
from myst.openapi.models.model_fit_policy_get import ModelFitPolicyGet


class ModelFitPolicyList(base_model.BaseModel):
    """Schema for model fit policy list responses."""

    data: List[ModelFitPolicyGet]
    has_more: bool
