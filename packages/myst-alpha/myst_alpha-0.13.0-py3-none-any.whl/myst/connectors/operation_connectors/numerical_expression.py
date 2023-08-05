from typing import List
from uuid import UUID

from myst.connectors.operation_connector import OperationConnector


class NumericalExpression(OperationConnector):
    def __init__(self, variable_names: List[str], math_expression: str) -> None:
        super().__init__(
            uuid=UUID("931acb25-7ace-47f9-9526-1ba8ddf06f14"),
            parameters=dict(variable_names=variable_names, math_expression=math_expression),
        )
