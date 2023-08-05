import enum
from typing import List
from uuid import UUID

from myst.connectors.source_connector import SourceConnector


@enum.unique
class Field(str, enum.Enum):
    APPARENT_TEMPERATURE_CELSIUS = "apparentTemperatureCelsius"
    CLOUD_COVERAGE_PERCENT = "cloudCoveragePercent"
    SURFACE_DEWPOINT_TEMPERATURE_CELSIUS = "surfaceDewpointTemperatureCelsius"
    DIFFUSE_HORIZONTAL_RADIATION_WSQM = "diffuseHorizontalRadiationWsqm"
    DIRECT_NORMAL_IRRADIANCE_WSQM = "directNormalIrradianceWsqm"
    DOWNWARD_SOLAR_RADIATION_WSQM = "downwardSolarRadiationWsqm"
    HEAT_INDEX_CELSIUS = "heatIndexCelsius"
    MSL_PRESSURE_KILOPASCALS = "mslPressureKilopascals"
    PRECIPITATION_PREVIOUS_HOUR_CENTIMETERS = "precipitationPreviousHourCentimeters"
    RELATIVE_HUMIDITY_PERCENT = "relativeHumidityPercent"
    SNOWFALL_CENTIMETERS = "snowfallCentimeters"
    SURFACE_AIR_PRESSURE_KILOPASCALS = "surfaceAirPressureKilopascals"
    SURFACE_TEMPERATURE_CELSIUS = "surfaceTemperatureCelsius"
    SURFACE_WIND_GUSTS_KPH = "surfaceWindGustsKph"
    SURFACE_WET_BULB_TEMPERATURE_CELSIUS = "surfaceWetBulbTemperatureCelsius"
    WIND_CHILL_TEMPERATURE_CELSIUS = "windChillTemperatureCelsius"
    WIND_DIRECTION_DEGREES = "windDirectionDegrees"
    WIND_SPEED_KPH = "windSpeedKph"


class CleanedObservations(SourceConnector):
    def __init__(self, latitude: float, longitude: float, fields: List[Field]) -> None:
        super().__init__(
            uuid=UUID("cfeb3606-217d-4fd0-9abf-21cd04a8e9e7"),
            parameters=dict(latitude=latitude, longitude=longitude, fields=fields),
        )
