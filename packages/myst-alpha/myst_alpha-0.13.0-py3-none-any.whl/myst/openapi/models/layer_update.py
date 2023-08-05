from typing import Any, List, Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.absolute_timing_create import AbsoluteTimingCreate
from myst.openapi.models.relative_timing_create import RelativeTimingCreate


class LayerUpdate(base_model.BaseModel):
    """Schema for layer update requests."""

    object_: Optional[Literal["Edge"]] = Field(..., alias="object")
    uuid: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    type: Optional[Literal["Layer"]] = None
    downstream_node: Optional[str] = None
    upstream_node: Optional[str] = None
    output_index: Optional[int] = None
    label_indexer: Optional[Union[List[Union[int, str, List[Any]]], List[Any], int, str]] = None
    order: Optional[int] = None
    start_timing: Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate]] = None
    end_timing: Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate]] = None
