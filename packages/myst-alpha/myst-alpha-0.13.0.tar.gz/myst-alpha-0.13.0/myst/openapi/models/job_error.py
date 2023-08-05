from typing import Optional

from myst.models import base_model


class JobError(base_model.BaseModel):
    """"""

    node: str
    reason: str
    edge: Optional[str] = None
