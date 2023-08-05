from typing import List

from myst.models import base_model
from myst.openapi.models.model_run_result_list_item import ModelRunResultListItem


class ModelRunResultList(base_model.BaseModel):
    """Schema for model run result list responses."""

    data: List[ModelRunResultListItem]
    has_more: bool
