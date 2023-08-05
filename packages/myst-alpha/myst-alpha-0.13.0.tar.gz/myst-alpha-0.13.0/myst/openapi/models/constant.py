from typing import Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class Constant(base_model.BaseModel):
    """"""

    object_: Literal["Sampler"] = Field(..., alias="object")
    type: Literal["Constant"]
    value: Union[float, int, str]
