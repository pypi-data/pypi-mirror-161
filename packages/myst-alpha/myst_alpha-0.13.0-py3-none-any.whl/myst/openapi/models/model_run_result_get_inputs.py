from typing import Any, Dict

from myst.models import base_model


class ModelRunResultGetInputs(base_model.BaseModel):
    """The input data that was used to create the outputs of this result."""

    __root__: Dict[str, Any]

    def __getitem__(self, item: str) -> Any:
        return self.__root__[item]
