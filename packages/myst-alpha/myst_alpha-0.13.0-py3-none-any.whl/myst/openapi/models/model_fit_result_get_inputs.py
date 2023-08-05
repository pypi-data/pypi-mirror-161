from typing import Any, Dict

from myst.models import base_model


class ModelFitResultGetInputs(base_model.BaseModel):
    """The data that was used to calculate this result."""

    __root__: Dict[str, Any]

    def __getitem__(self, item: str) -> Any:
        return self.__root__[item]
