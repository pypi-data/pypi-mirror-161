import enum
from typing import List
from uuid import UUID

from myst.connectors.operation_connector import OperationConnector


@enum.unique
class GroupName(str, enum.Enum):
    OPERANDS = "operands"


class GetDummies(OperationConnector):
    def __init__(self, categories: List[int]) -> None:
        super().__init__(uuid=UUID("5c1b5c26-7a76-4f95-a38b-9c92b3830a1b"), parameters=dict(categories=categories))
