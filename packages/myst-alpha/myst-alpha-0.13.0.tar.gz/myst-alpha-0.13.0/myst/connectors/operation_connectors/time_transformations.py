import enum
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from myst.connectors.operation_connector import OperationConnector
from myst.core.time.time_delta import TimeDelta


@enum.unique
class GroupName(str, enum.Enum):
    OPERANDS = "operands"


@enum.unique
class AggregationFunction(str, enum.Enum):
    COUNT = "count"
    SUM = "sum"
    MEAN = "mean"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"


@dataclass
class RollingWindowParameters:
    window_period: TimeDelta
    min_periods: int
    centered: bool
    aggregation_function: AggregationFunction


@dataclass
class DifferencingParameters:
    differencing_period: Optional[TimeDelta] = None
    differencing_order: Optional[int] = None


@dataclass
class ShiftParameters:
    shift_period: Optional[TimeDelta] = None


class TimeTransformations(OperationConnector):
    def __init__(
        self,
        rolling_window_parameters: Optional[RollingWindowParameters] = None,
        differencing_parameters: Optional[DifferencingParameters] = None,
        shift_parameters: Optional[ShiftParameters] = None,
    ) -> None:
        super().__init__(
            uuid=UUID("e4bebd6d-d9d2-4103-8c94-95fa162eddc0"),
            parameters=dict(
                rolling_window_parameters=rolling_window_parameters,
                differencing_parameters=differencing_parameters,
                shift_parameters=shift_parameters,
            ),
        )
