from typing import Any, List, Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.absolute_timing_get import AbsoluteTimingGet
from myst.openapi.models.relative_timing_get import RelativeTimingGet


class LayerGet(base_model.BaseModel):
    """Schema for layer get responses."""

    object_: Literal["Edge"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["Layer"]
    downstream_node: str
    upstream_node: str
    output_index: int
    order: int
    update_time: Optional[str] = None
    label_indexer: Optional[Union[List[Union[int, str, List[Any]]], List[Any], int, str]] = None
    start_timing: Optional[Union[AbsoluteTimingGet, RelativeTimingGet]] = None
    end_timing: Optional[Union[AbsoluteTimingGet, RelativeTimingGet]] = None
