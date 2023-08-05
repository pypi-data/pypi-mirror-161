from typing import Any, List, Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class InputGet(base_model.BaseModel):
    """Schema for input get responses."""

    object_: Literal["Edge"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["Input"]
    downstream_node: str
    upstream_node: str
    output_index: int
    group_name: str
    update_time: Optional[str] = None
    label_indexer: Optional[Union[List[Union[int, str, List[Any]]], List[Any], int, str]] = None
