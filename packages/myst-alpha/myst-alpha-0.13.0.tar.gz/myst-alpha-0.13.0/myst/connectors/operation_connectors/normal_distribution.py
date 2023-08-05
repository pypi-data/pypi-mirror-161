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


class NormalDistribution(OperationConnector):
    def __init__(self, function: Function, value: float) -> None:
        super().__init__(
            uuid=UUID("b5bee009-db1c-448a-b701-e0345a96db6b"), parameters=dict(function=function, value=value)
        )
