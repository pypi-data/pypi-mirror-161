from typing import Optional

from myst.models import base_model


class HPOMetrics(base_model.BaseModel):
    """The set of metrics produced by an HPO trial."""

    mae: float
    mse: float
    mape: Optional[float] = None
