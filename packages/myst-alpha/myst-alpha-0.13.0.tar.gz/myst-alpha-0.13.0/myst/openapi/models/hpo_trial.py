from typing import Any, Dict

from myst.models import base_model
from myst.openapi.models.hpo_metrics import HPOMetrics


class HPOTrial(base_model.BaseModel):
    """Represents the result of a single HPO trial."""

    parameters: Dict[str, Any]
    metrics: HPOMetrics
