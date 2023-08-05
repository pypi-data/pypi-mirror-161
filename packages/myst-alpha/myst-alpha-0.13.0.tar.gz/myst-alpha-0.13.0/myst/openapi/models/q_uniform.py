from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class QUniform(base_model.BaseModel):
    """"""

    object_: Literal["Sampler"] = Field(..., alias="object")
    type: Literal["QUniform"]
    lower: float
    upper: float
    q: float
