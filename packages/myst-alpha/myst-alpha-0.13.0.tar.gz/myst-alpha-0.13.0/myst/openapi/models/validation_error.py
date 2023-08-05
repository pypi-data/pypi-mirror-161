from typing import List

from myst.models import base_model


class ValidationError(base_model.BaseModel):
    """"""

    loc: List[str]
    msg: str
    type: str
