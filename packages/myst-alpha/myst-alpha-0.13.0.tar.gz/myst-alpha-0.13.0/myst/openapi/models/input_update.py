from typing import Any, List, Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class InputUpdate(base_model.BaseModel):
    """Schema for input update requests."""

    object_: Optional[Literal["Edge"]] = Field(..., alias="object")
    uuid: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    type: Optional[Literal["Input"]] = None
    downstream_node: Optional[str] = None
    upstream_node: Optional[str] = None
    output_index: Optional[int] = None
    label_indexer: Optional[Union[List[Union[int, str, List[Any]]], List[Any], int, str]] = None
    group_name: Optional[str] = None
