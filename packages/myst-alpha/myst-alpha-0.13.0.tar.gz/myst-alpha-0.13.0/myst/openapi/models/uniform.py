from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class Uniform(base_model.BaseModel):
    """"""

    object_: Literal["Sampler"] = Field(..., alias="object")
    type: Literal["Uniform"]
    lower: float
    upper: float
