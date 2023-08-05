from typing import Any, Dict
from uuid import UUID


class Connector:
    """Base class for connectors."""

    def __init__(self, uuid: UUID, parameters: Dict[str, Any]) -> None:
        self._uuid = uuid
        self._parameters = parameters

    @property
    def uuid(self) -> UUID:
        return self._uuid

    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters

    def parameters_exclude_none(self) -> Dict[str, Any]:
        return {k: v for k, v in self.parameters.items() if v is not None}
