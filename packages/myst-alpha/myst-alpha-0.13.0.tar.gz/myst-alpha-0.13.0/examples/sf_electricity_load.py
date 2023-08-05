from uuid import UUID

import myst
from myst.connectors.model_connectors import xgboost
from myst.connectors.operation_connectors import time_transformations
from myst.connectors.source_connector import SourceConnector
from myst.connectors.source_connectors import cleaned_observations, enhanced_forecast, historical_hourly_conditions

myst.authenticate()

project = myst.Project.create(title="SF Electricity Load")

ksfo_cleaned_observations = project.create_source(
    title="Cleaned Weather (KSFO)",
    connector=cleaned_observations.CleanedObservations(
        latitude=37.619,
        longitude=-122.374,
        fields=[
            cleaned_observations.Field.RELATIVE_HUMIDITY_PERCENT,
            cleaned_observations.Field.SURFACE_TEMPERATURE_CELSIUS,
        ],
    ),
)

ksfo_hhc = project.create_source(
    title="Historical Weather (KSFO)",
    connector=historical_hourly_conditions.HistoricalHourlyConditions(
        latitude=37.619,
        longitude=-122.374,
        fields=[historical_hourly_conditions.Field.RELATIVE_HUMIDITY, historical_hourly_conditions.Field.TEMPERATURE],
    ),
)

# If a connector isn't present in the library yet, you can still specify it and its parameters. This is The Weather
# Company's Enhanced Forecast API.
ksfo_forecast = project.create_source(
    title="Forecasted Weather (KSFO)",
    connector=SourceConnector(
        uuid=UUID("1aeaadec-6912-422a-a4fc-5d6765391c17"),
        parameters=dict(latitude=37.619, longitude=-122.374, fields=["relativeHumidity", "temperature"]),
    ),
)

ksfo_temperature_ts = project.create_time_series(title="Temperature (KSFO)", sample_period=myst.TimeDelta("PT1H"))

# Add the three weather sources to the temperature time series.
ksfo_temperature_ts.create_layer(
    node=ksfo_cleaned_observations,
    order=0,
    end_timing=myst.TimeDelta("-PT23H"),
    label_indexer=cleaned_observations.Field.SURFACE_TEMPERATURE_CELSIUS.value,
)
ksfo_temperature_ts.create_layer(
    node=ksfo_hhc,
    order=1,
    start_timing=myst.TimeDelta("-PT23H"),
    end_timing=myst.TimeDelta("PT1H"),
    label_indexer=historical_hourly_conditions.Field.TEMPERATURE.value,
)
ksfo_temperature_ts.create_layer(
    node=ksfo_forecast,
    order=2,
    start_timing=myst.TimeDelta("PT1H"),
    label_indexer=enhanced_forecast.Field.TEMPERATURE.value,
)

assert [layer.upstream_node for layer in ksfo_temperature_ts.list_layers()] == [
    ksfo_cleaned_observations.uuid,
    ksfo_hhc.uuid,
    ksfo_forecast.uuid,
]

# Create a 3-hour rolling mean of temperature.
rolling_mean_op = project.create_operation(
    title="Temperature (KSFO) - 3H Rolling Mean",
    connector=time_transformations.TimeTransformations(
        rolling_window_parameters=time_transformations.RollingWindowParameters(
            window_period=myst.TimeDelta("PT3H"),
            min_periods=1,
            centered=False,
            aggregation_function=time_transformations.AggregationFunction.MEAN,
        )
    ),
)

rolling_mean_op.create_input(time_series=ksfo_temperature_ts, group_name=time_transformations.GroupName.OPERANDS)

ksfo_rolling_mean_temp = project.create_time_series(
    title="Temperature (KSFO) - Rolling 3H Mean", sample_period=myst.TimeDelta("PT1H")
)

ksfo_rolling_mean_temp.create_layer(node=rolling_mean_op, order=0)

historical_sf_electricity_load = project.create_time_series(
    title="Historical SF Electricity Load",
    sample_period=myst.TimeDelta("PT1H"),
    description="Historical SF electricity load (target), to be uploaded into the platform",
)

xgboost_model = project.create_model(title="XGBoost Model", connector=xgboost.XGBoost())

xgboost_model.create_input(time_series=ksfo_rolling_mean_temp, group_name=xgboost.GroupName.FEATURES)

xgboost_model.create_input(time_series=historical_sf_electricity_load, group_name=xgboost.GroupName.TARGETS)

forecast_sf_electricity_load = project.create_time_series(
    title="Forecasted SF Electricity Load", sample_period=myst.TimeDelta("PT1H")
)

forecast_sf_electricity_load.create_layer(node=xgboost_model, order=0)

xgboost_model_fit_policy = xgboost_model.create_fit_policy(
    schedule_timing=myst.TimeDelta("PT24H"),
    start_timing=myst.Time("2021-01-01T00:00:00Z"),
    end_timing=myst.TimeDelta("-PT1H"),
)

forecast_prediction_policy = forecast_sf_electricity_load.create_run_policy(
    schedule_timing=myst.TimeDelta("PT1H"), start_timing=myst.TimeDelta("PT1H"), end_timing=myst.TimeDelta("P7D")
)
