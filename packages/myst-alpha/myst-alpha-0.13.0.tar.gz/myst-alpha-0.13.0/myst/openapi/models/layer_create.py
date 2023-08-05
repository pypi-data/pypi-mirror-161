from typing import Any, List, Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.absolute_timing_create import AbsoluteTimingCreate
from myst.openapi.models.relative_timing_create import RelativeTimingCreate


class LayerCreate(base_model.BaseModel):
    """Schema for layer create requests."""

    upstream_node: str
    order: int
    object_: Optional[Literal["Edge"]] = Field("Edge", alias="object")
    type: Optional[Literal["Layer"]] = "Layer"
    output_index: Optional[int] = 0
    label_indexer: Optional[Union[List[Union[int, str, List[Any]]], List[Any], int, str]] = None
    start_timing: Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate]] = None
    end_timing: Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate]] = None
