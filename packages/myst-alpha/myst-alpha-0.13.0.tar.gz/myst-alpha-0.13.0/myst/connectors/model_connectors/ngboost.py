import enum
from typing import Optional
from uuid import UUID

from myst.connectors.model_connector import ModelConnector


@enum.unique
class GroupName(str, enum.Enum):
    FEATURES = "features"
    TARGETS = "targets"
    SAMPLE_WEIGHTS = "sample_weights"


@enum.unique
class LabelIndexer(str, enum.Enum):
    LOC = "loc"
    SCALE = "scale"


@enum.unique
class NGBoostDistribution(str, enum.Enum):
    CAUCHY = "Cauchy"
    LAPLACE = "Laplace"
    LOG_NORMAL = "LogNormal"
    NORMAL = "Normal"


class NGBoost(ModelConnector):
    def __init__(
        self,
        distribution: Optional[NGBoostDistribution] = None,
        n_estimators: Optional[int] = None,
        learning_rate: Optional[float] = None,
        minibatch_frac: Optional[float] = None,
        col_sample: Optional[float] = None,
        max_depth: Optional[float] = None,
    ) -> None:
        super().__init__(
            uuid=UUID("7138f288-b588-456f-8164-026d9dea810b"),
            parameters=dict(
                distribution=distribution,
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                minibatch_frac=minibatch_frac,
                col_sample=col_sample,
                max_depth=max_depth,
            ),
        )
