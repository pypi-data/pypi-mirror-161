from typing import Any, Dict

from myst.models import base_model


class BacktestResultGetMetrics(base_model.BaseModel):
    """"""

    __root__: Dict[str, Any]

    def __getitem__(self, item: str) -> Any:
        return self.__root__[item]
