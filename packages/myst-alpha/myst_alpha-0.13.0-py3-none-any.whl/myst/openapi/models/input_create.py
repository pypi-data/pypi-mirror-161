from typing import Any, List, Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class InputCreate(base_model.BaseModel):
    """Schema for input create requests."""

    upstream_node: str
    group_name: str
    object_: Optional[Literal["Edge"]] = Field("Edge", alias="object")
    type: Optional[Literal["Input"]] = "Input"
    output_index: Optional[int] = 0
    label_indexer: Optional[Union[List[Union[int, str, List[Any]]], List[Any], int, str]] = None
