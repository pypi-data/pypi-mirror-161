from typing import Any, Dict

from myst.models import base_model


class ModelGetInputSpecsSchema(base_model.BaseModel):
    """A JSON Schema definition describing the inputs that this model can be used with. Output only."""

    __root__: Dict[str, Any]

    def __getitem__(self, item: str) -> Any:
        return self.__root__[item]
