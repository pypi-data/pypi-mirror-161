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


class LaplaceDistribution(OperationConnector):
    def __init__(self, function: Function, value: float) -> None:
        super().__init__(
            uuid=UUID("fe0bf54d-183a-4846-848e-2d0355f45afd"), parameters=dict(function=function, value=value)
        )
