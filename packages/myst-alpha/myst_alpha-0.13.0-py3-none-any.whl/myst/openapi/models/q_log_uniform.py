from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class QLogUniform(base_model.BaseModel):
    """"""

    object_: Literal["Sampler"] = Field(..., alias="object")
    type: Literal["QLogUniform"]
    lower: float
    upper: float
    q: float
    base: Optional[int] = 10
