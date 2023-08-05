import enum
from typing import Optional
from uuid import UUID

from myst.connectors.model_connector import ModelConnector


@enum.unique
class GroupName(str, enum.Enum):
    FEATURES = "features"
    TARGETS = "targets"


class ElasticNet(ModelConnector):
    def __init__(
        self,
        alpha: Optional[float] = None,
        l1_ratio: Optional[float] = None,
        fit_intercept: Optional[bool] = None,
        max_iter: Optional[int] = None,
    ) -> None:
        super().__init__(
            uuid=UUID("f2aaf05d-4fb4-4106-979e-a1ebd36efb2b"),
            parameters=dict(alpha=alpha, l1_ratio=l1_ratio, fit_intercept=fit_intercept, max_iter=max_iter),
        )
