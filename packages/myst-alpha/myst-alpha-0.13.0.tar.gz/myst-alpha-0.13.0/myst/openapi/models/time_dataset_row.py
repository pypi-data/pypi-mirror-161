from typing import List, Optional

from myst.models import base_model


class TimeDatasetRow(base_model.BaseModel):
    """"""

    start_time: str
    end_time: str
    as_of_time: str
    values: List[float]
    mask: Optional[List[float]] = None
