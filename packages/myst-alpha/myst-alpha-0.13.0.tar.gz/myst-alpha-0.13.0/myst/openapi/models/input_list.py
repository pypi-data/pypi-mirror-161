from typing import List

from myst.models import base_model
from myst.openapi.models.input_get import InputGet


class InputList(base_model.BaseModel):
    """Schema for input list responses."""

    data: List[InputGet]
    has_more: bool
