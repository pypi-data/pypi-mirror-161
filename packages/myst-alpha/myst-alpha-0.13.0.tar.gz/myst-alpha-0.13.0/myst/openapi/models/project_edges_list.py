from typing import List, Union

from myst.models import base_model
from myst.openapi.models.input_get import InputGet
from myst.openapi.models.layer_get import LayerGet


class ProjectEdgesList(base_model.BaseModel):
    """Project edges list schema."""

    data: List[Union[InputGet, LayerGet]]
    has_more: bool
