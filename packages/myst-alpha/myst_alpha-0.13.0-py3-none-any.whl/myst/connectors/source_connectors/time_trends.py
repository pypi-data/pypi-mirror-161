import enum
from typing import List
from uuid import UUID

from myst.connectors.source_connector import SourceConnector
from myst.core.time.time_delta import TimeDelta


@enum.unique
class Field(str, enum.Enum):
    CALENDAR_YEAR = "CALENDAR_YEAR"
    DAY_OF_WEEK = "DAY_OF_WEEK"
    DAY_OF_YEAR = "DAY_OF_YEAR"
    HOUR_OF_DAY = "HOUR_OF_DAY"
    IS_WEEKDAY = "IS_WEEKDAY"
    MONTH_OF_YEAR = "MONTH_OF_YEAR"
    WEEK_OF_YEAR = "WEEK_OF_YEAR"
    EPOCH = "EPOCH"


class TimeTrends(SourceConnector):
    def __init__(self, sample_period: TimeDelta, time_zone: str, fields: List[Field]) -> None:
        super().__init__(
            uuid=UUID("7621e074-3d62-4735-911d-91a2a971240d"),
            parameters=dict(sample_period=sample_period, time_zone=time_zone, fields=fields),
        )
