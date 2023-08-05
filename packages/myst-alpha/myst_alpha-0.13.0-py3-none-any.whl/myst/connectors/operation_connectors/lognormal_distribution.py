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


class LogNormalDistribution(OperationConnector):
    def __init__(self, function: Function, value: float) -> None:
        super().__init__(
            uuid=UUID("9f0349d4-d272-4f45-b2e1-2957bc5a1a1f"), parameters=dict(function=function, value=value)
        )
