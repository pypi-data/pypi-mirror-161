import enum
from uuid import UUID

from myst.connectors.operation_connector import OperationConnector


@enum.unique
class GroupName(str, enum.Enum):
    LOC = "loc"
    SCALE = "scale"


@enum.unique
class Function(str, enum.Enum):
    CDF = "CDF"
    PDF = "PDF"
    PPF = "PPF"


class CauchyDistribution(OperationConnector):
    def __init__(self, function: Function, value: float) -> None:
        super().__init__(
            uuid=UUID("babb2dbf-e616-422f-aa76-14c6e60d42ae"), parameters=dict(function=function, value=value)
        )
