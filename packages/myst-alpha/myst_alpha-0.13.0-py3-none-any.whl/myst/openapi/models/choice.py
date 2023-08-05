from typing import List, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class Choice(base_model.BaseModel):
    """"""

    object_: Literal["Sampler"] = Field(..., alias="object")
    type: Literal["Choice"]
    choices: List[Union[float, int, str]]
