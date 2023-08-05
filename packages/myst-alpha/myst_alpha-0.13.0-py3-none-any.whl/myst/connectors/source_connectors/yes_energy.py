import enum
from dataclasses import dataclass
from typing import List
from uuid import UUID

from myst.connectors.source_connector import SourceConnector


@enum.unique
class YesEnergyAggregation(str, enum.Enum):
    AVG = "AVG"
    MAX = "MAX"
    MIN = "MIN"


@dataclass
class YesEnergyItem:
    datatype: str
    object_id: int


class YesEnergy(SourceConnector):
    def __init__(self, items: List[YesEnergyItem], stat: YesEnergyAggregation = YesEnergyAggregation.AVG) -> None:
        super().__init__(uuid=UUID("207da43c-d284-44ee-90d0-61b96fa4df1c"), parameters=dict(items=items, stat=stat))
