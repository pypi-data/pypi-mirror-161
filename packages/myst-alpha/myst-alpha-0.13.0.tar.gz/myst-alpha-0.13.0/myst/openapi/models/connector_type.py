from enum import Enum


class ConnectorType(str, Enum):
    SOURCE = "source"
    OPERATION = "operation"
    MODEL = "model"

    def __str__(self) -> str:
        return str(self.value)
