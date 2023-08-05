import enum
from typing import List
from uuid import UUID

from myst.connectors.source_connector import SourceConnector


@enum.unique
class Field(str, enum.Enum):
    CLOUD_COVER = "cloudCover"
    PRECIP_CHANCE = "precipChance"
    PRECIP_TYPE = "precipType"
    PRESSURE_MEAN_SEA_LEVEL = "pressureMeanSeaLevel"
    QPF = "qpf"
    QPF_SNOW = "qpfSnow"
    RELATIVE_HUMIDITY = "relativeHumidity"
    TEMPERATURE = "temperature"
    TEMPERATURE_DEW_POINT = "temperatureDewPoint"
    TEMPERATURE_FEELS_LIKE = "temperatureFeelsLike"
    TEMPERATURE_HEAT_INDEX = "temperatureHeatIndex"
    TEMPERATURE_WIND_CHILL = "temperatureWindChill"
    UV_INDEX = "uvIndex"
    VISIBILITY = "visibility"
    WIND_DIRECTION = "windDirection"
    WIND_GUST = "windGust"
    WIND_SPEED = "windSpeed"


class EnhancedForecast(SourceConnector):
    def __init__(self, latitude: float, longitude: float, fields: List[Field]) -> None:
        super().__init__(
            uuid=UUID("1aeaadec-6912-422a-a4fc-5d6765391c17"),
            parameters=dict(latitude=latitude, longitude=longitude, fields=fields),
        )
