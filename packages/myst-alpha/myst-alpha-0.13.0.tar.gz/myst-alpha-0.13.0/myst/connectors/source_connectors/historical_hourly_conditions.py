import enum
from typing import List
from uuid import UUID

from myst.connectors.source_connector import SourceConnector


@enum.unique
class Field(str, enum.Enum):
    CLOUD_CEILING = "cloudCeiling"
    CLOUD_COVERAGE_PERCENT = "cloudCoveragePercent"
    EXPIRATION_TIME_UTC = "expirationTimeUtc"
    ICON_CODE = "iconCode"
    ICON_CODE_EXTEND = "iconCodeExtend"
    PRECIP_24_HOUR = "precip24Hour"
    PRESSURE_ALTIMETER = "pressureAltimeter"
    PRESSURE_CHANGE = "pressureChange"
    PRESSURE_MEAN_SEA_LEVEL = "pressureMeanSeaLevel"
    PRESSURE_TENDENCY_CODE = "pressureTendencyCode"
    RELATIVE_HUMIDITY = "relativeHumidity"
    SNOW_24_HOUR = "snow24Hour"
    SUNRISE_TIME_UTC = "sunriseTimeUtc"
    SUNSET_TIME_UTC = "sunsetTimeUtc"
    TEMPERATURE = "temperature"
    TEMPERATURE_CHANGE_24_HOUR = "temperatureChange24Hour"
    TEMPERATURE_DEW_POINT = "temperatureDewPoint"
    TEMPERATURE_FEELS_LIKE = "temperatureFeelsLike"
    TEMPERATURE_HEAT_INDEX = "temperatureHeatIndex"
    TEMPERATURE_MAX_24_HOUR = "temperatureMax24Hour"
    TEMPERATURE_MAX_SINCE_7_AM = "temperatureMaxSince7Am"
    TEMPERATURE_MIN_24_HOUR = "temperatureMin24Hour"
    TEMPERATURE_WIND_CHILL = "temperatureWindChill"
    UV_INDEX = "uvIndex"
    VALID_TIME_UTC = "validTimeUtc"
    VISIBILITY = "visibility"
    WIND_DIRECTION = "windDirection"
    WIND_GUST = "windGust"
    WIND_SPEED = "windSpeed"


class HistoricalHourlyConditions(SourceConnector):
    def __init__(self, latitude: float, longitude: float, fields: List[Field]) -> None:
        super().__init__(
            uuid=UUID("6f2851e1-7612-4276-a864-172d8c1a060c"),
            parameters=dict(latitude=latitude, longitude=longitude, fields=fields),
        )
