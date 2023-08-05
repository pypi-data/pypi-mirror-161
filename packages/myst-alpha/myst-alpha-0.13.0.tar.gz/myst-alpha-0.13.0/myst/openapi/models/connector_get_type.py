from enum import Enum


class ConnectorGetType(str, Enum):
    SOURCECONNECTOR = "SourceConnector"
    OPERATIONCONNECTOR = "OperationConnector"
    MODELCONNECTOR = "ModelConnector"

    def __str__(self) -> str:
        return str(self.value)
