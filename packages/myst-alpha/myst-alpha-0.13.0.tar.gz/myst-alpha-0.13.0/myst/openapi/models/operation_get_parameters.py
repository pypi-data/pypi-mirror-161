from typing import Any, Dict

from myst.models import base_model


class OperationGetParameters(base_model.BaseModel):
    """The parameters used in the node's connector. Must adhere to connector's parameter schema."""

    __root__: Dict[str, Any]

    def __getitem__(self, item: str) -> Any:
        return self.__root__[item]
