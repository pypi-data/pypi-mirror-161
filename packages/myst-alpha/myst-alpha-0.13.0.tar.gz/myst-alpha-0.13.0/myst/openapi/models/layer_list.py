from typing import List

from myst.models import base_model
from myst.openapi.models.layer_get import LayerGet


class LayerList(base_model.BaseModel):
    """Schema for layer list responses."""

    data: List[LayerGet]
    has_more: bool
