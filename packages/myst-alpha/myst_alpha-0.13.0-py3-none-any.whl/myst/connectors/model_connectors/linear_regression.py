import enum
from uuid import UUID

from myst.connectors.model_connector import ModelConnector


@enum.unique
class GroupName(str, enum.Enum):
    FEATURES = "features"
    TARGETS = "targets"
    SAMPLE_WEIGHTS = "sample_weights"


class LinearRegression(ModelConnector):
    def __init__(self, fit_intercept: bool = True, normalize: bool = False) -> None:
        super().__init__(
            uuid=UUID("7b714851-bfbf-46a2-a8e5-8af90b8bae71"),
            parameters=dict(fit_intercept=fit_intercept, normalize=normalize),
        )
