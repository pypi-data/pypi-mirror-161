from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class LogUniform(base_model.BaseModel):
    """Represents a uniform distribution of values on a logarithmic scale."""

    object_: Literal["Sampler"] = Field(..., alias="object")
    type: Literal["LogUniform"]
    lower: float
    upper: float
    base: Optional[int] = 10
