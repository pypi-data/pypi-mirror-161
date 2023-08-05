from typing import List

from myst.models import base_model
from myst.openapi.models.model_fit_result_list_item import ModelFitResultListItem


class ModelFitResultList(base_model.BaseModel):
    """Schema for model fit result list responses."""

    data: List[ModelFitResultListItem]
    has_more: bool
