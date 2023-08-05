import enum
from uuid import UUID

from myst.connectors.operation_connector import OperationConnector


@enum.unique
class GroupName(str, enum.Enum):
    OPERANDS = "operands"


class FillNA(OperationConnector):
    def __init__(self, value: float) -> None:
        super().__init__(uuid=UUID("f268a5d7-dc66-4dc8-a053-4d50e9866611"), parameters=dict(value=value))
