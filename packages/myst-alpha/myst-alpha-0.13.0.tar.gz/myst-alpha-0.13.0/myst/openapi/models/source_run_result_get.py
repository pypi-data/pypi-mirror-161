from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class SourceRunResultGet(base_model.BaseModel):
    """Schema for source run result get responses."""

    object_: Literal["NodeResult"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["SourceRunResult"]
    node: str
    start_time: str
    end_time: str
    as_of_time: str
    update_time: Optional[str] = None
