import enum
from uuid import UUID

from myst.connectors.operation_connector import OperationConnector
from myst.core.time.time_delta import TimeDelta


@enum.unique
class GroupName(str, enum.Enum):
    OPERANDS = "operands"


@enum.unique
class ResamplingFunction(str, enum.Enum):
    INTERPOLATE = "interpolate"
    PAD = "pad"
    FIRST = "first"
    LAST = "last"
    MEAN = "mean"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    SUM = "sum"


class Resampling(OperationConnector):
    def __init__(self, sample_period: TimeDelta, resampling_function: ResamplingFunction) -> None:
        super().__init__(
            uuid=UUID("7d6d92d6-5fc2-47b7-9f3c-7ae73cf30b7f"),
            parameters=dict(sample_period=sample_period, resampling_function=resampling_function),
        )
