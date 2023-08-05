from typing import Any, Dict

from myst.models import base_model


class OperationConnectorGetParametersSchema(base_model.BaseModel):
    """The schema for the parameters of this connector."""

    __root__: Dict[str, Any]

    def __getitem__(self, item: str) -> Any:
        return self.__root__[item]
