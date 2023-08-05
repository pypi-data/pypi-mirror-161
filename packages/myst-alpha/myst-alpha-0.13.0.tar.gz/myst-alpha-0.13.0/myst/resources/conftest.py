from typing import Any, Dict, Generator

import pytest
from respx import MockRouter

import myst
from myst.auth.credentials import FakeCredentials


@pytest.fixture(scope="module", autouse=True)
def use_fake_credentials() -> None:
    myst.set_client(myst.Client(credentials=FakeCredentials()))


@pytest.fixture(autouse=True)
def mock_api() -> Generator[MockRouter, None, None]:
    with MockRouter(base_url=f"{myst.settings.MYST_API_HOST}/v1alpha2/") as mock_router:
        yield mock_router


@pytest.fixture
def example_project() -> Dict[str, Any]:
    return dict(
        object="Project",
        uuid="7c1ccecc-f03b-4f33-95bf-581ee96a900e",
        create_time="2021-09-15T23:35:00Z",
        update_time=None,
        organization="f02caef7-07a4-4c47-8901-9680c2124f2e",
        organization_sharing_enabled=False,
        owner="e4769980-e154-4b10-96b7-ca9f72671843",
        title="uncontradictious-crassina-talemonger-euphroe",
        description="Some test project.",
        creator="e4769980-e154-4b10-96b7-ca9f72671843",
        deploy_status="NEW",
    )


@pytest.fixture
def example_source(example_project: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Node",
        uuid="b13ffa7b-1bf2-4ed5-bf96-8701df9e1b1c",
        create_time="2021-09-15T22:36:17Z",
        update_time=None,
        organization="99799474-bc23-4026-ae88-89471a077b69",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        type="Source",
        title="Forecasted Weather in SF",
        description=None,
        project=example_project["uuid"],
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        deploy_status="NEW",
        connector_uuid="1aeaadec-6912-422a-a4fc-5d6765391c17",
        parameters=dict(latitude=37.7948, longitude=-122.3986, fields=["relativeHumidity", "temperature"]),
    )


@pytest.fixture
def example_model(example_project: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Node",
        uuid="36cad5b7-6ea8-4e08-9546-d28218e2486f",
        create_time="2021-09-15T22:36:35Z",
        update_time=None,
        organization="99799474-bc23-4026-ae88-89471a077b69",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        type="Model",
        title="An XGBoost Model",
        description=None,
        project=example_project["uuid"],
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        deploy_status="NEW",
        connector_uuid="b78ff94a-27b1-4986-a88a-536661239bb2",
        input_specs_schema=dict(foo="bar"),
        parameters=dict(
            num_boost_round=10,
            max_depth=6,
            min_child_weight=1,
            learning_rate=0.3,
            subsample=1.0,
            colsample_bytree=1.0,
            colsample_bylevel=1.0,
            colsample_bynode=1.0,
            gamma=0.0,
            reg_alpha=0.0,
            reg_lambda=1.0,
        ),
    )


@pytest.fixture
def example_operation(example_project: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Node",
        uuid="d0f21c98-b6c5-42ba-98c8-6d336f6be4be",
        create_time="2021-09-15T22:36:30Z",
        update_time=None,
        organization="99799474-bc23-4026-ae88-89471a077b69",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        type="Operation",
        title="3H Rolling Mean",
        description="Takes a rolling mean of the upstream series",
        project=example_project["uuid"],
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        deploy_status="NEW",
        connector_uuid="e4bebd6d-d9d2-4103-8c94-95fa162eddc0",
        input_specs_schema=dict(foo="bar"),
        parameters=dict(
            rolling_window_parameters=dict(
                window_period="PT3H", min_periods=1, centered=False, aggregation_function="mean"
            ),
            differencing_parameters=None,
            shift_parameters=None,
        ),
    )


@pytest.fixture
def example_time_series(example_project: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Node",
        uuid="221c85ec-0bf1-477c-a820-ce0da7dd6f04",
        create_time="2021-09-15T22:36:42Z",
        update_time=None,
        organization="99799474-bc23-4026-ae88-89471a077b69",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        type="TimeSeries",
        title="The thing we want to predict",
        description="This is a time series",
        project=example_project["uuid"],
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        deploy_status="NEW",
        sample_period="PT1H",
        cell_shape=[2, 3],
        coordinate_labels=[["x1", "x2"], ["y1", "y2", "y3"]],
        axis_labels=["x", "y"],
    )


@pytest.fixture
def example_model_input(example_model: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Edge",
        uuid="ceb01ff3-badf-4829-9322-911168d502aa",
        create_time="2021-09-15T22:36:36Z",
        update_time=None,
        type="Input",
        project=example_model["project"],
        downstream_node=example_model["uuid"],
        upstream_node="e6af86ed-850c-484d-898e-72a53b4ffe7f",
        output_index=0,
        label_indexer=None,
        group_name="features",
    )


@pytest.fixture
def example_operation_input(example_operation: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Edge",
        uuid="8046a461-b58d-40fe-ae4a-079ff2f9c213",
        create_time="2021-09-15T22:36:31Z",
        update_time=None,
        type="Input",
        project=example_operation["project"],
        downstream_node=example_operation["uuid"],
        upstream_node="d4d750fe-f727-4073-b6d9-8c643476ac93",
        output_index=0,
        label_indexer=None,
        group_name="operands",
    )


@pytest.fixture
def example_layer(example_time_series: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Edge",
        uuid="e09ee995-1aaa-4ad3-b91a-925b8f0a4679",
        create_time="2021-09-15T22:36:44Z",
        update_time=None,
        type="Layer",
        project=example_time_series["project"],
        downstream_node=example_time_series["uuid"],
        upstream_node="36cad5b7-6ea8-4e08-9546-d28218e2486f",
        output_index=0,
        label_indexer=None,
        order=0,
        start_timing=None,
        end_timing=None,
    )


@pytest.fixture
def example_backtest(example_project: Dict[str, Any], example_model: Dict[str, Any]) -> Dict[str, Any]:
    fit_start_timing_str = "-P1Y"
    fit_end_timing_str = "PT0H"
    predict_start_timing_str = "PT1H"
    predict_end_timing_str = "PT6H"

    return dict(
        object="Backtest",
        uuid="6c219892-5d88-40d8-85d4-56170f752336",
        project=example_project["uuid"],
        create_time="2021-09-15T22:36:44Z",
        update_time=None,
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        title="example_backtest",
        description=None,
        model=example_model["uuid"],
        test_start_time="2020-01-01T00:00:00Z",
        test_end_time="2021-01-01T00:00:00Z",
        fit_start_timing=dict(object="Timing", type="RelativeTiming", offset=fit_start_timing_str, time_zone=None),
        fit_end_timing=dict(object="Timing", type="RelativeTiming", offset=fit_end_timing_str, time_zone=None),
        fit_reference_timing=dict(object="Timing", type="CronTiming", cron_expression="0 0 * * 0", time_zone="UTC"),
        predict_start_timing=dict(
            object="Timing", type="RelativeTiming", offset=predict_start_timing_str, time_zone="UTC"
        ),
        predict_end_timing=dict(object="Timing", type="RelativeTiming", offset=predict_end_timing_str, time_zone="UTC"),
        predict_reference_timing=dict(object="Timing", type="CronTiming", cron_expression="0 * * * *", time_zone="UTC"),
    )


@pytest.fixture
def example_hpo(example_project: Dict[str, Any], example_model: Dict[str, Any]) -> Dict[str, Any]:
    fit_start_timing_str = "-P1Y"
    fit_end_timing_str = "PT0H"
    predict_start_timing_str = "PT1H"
    predict_end_timing_str = "PT6H"

    return dict(
        object="HPO",
        uuid="c72c0a3d-7690-4b22-bafb-267437a1e648",
        project=example_project["uuid"],
        create_time="2021-09-15T22:36:44Z",
        update_time=None,
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        title="example_hpo",
        description=None,
        model=example_model["uuid"],
        test_start_time="2020-01-01T00:00:00Z",
        test_end_time="2021-01-01T00:00:00Z",
        fit_start_timing=dict(object="Timing", type="RelativeTiming", offset=fit_start_timing_str, time_zone=None),
        fit_end_timing=dict(object="Timing", type="RelativeTiming", offset=fit_end_timing_str, time_zone=None),
        fit_reference_timing=dict(object="Timing", type="CronTiming", cron_expression="0 0 * * 0", time_zone="UTC"),
        predict_start_timing=dict(
            object="Timing", type="RelativeTiming", offset=predict_start_timing_str, time_zone="UTC"
        ),
        predict_end_timing=dict(object="Timing", type="RelativeTiming", offset=predict_end_timing_str, time_zone="UTC"),
        predict_reference_timing=dict(object="Timing", type="CronTiming", cron_expression="0 * * * *", time_zone="UTC"),
        search_algorithm=dict(
            object="SearchAlgorithm", type="Hyperopt", metric="mse", num_trials=12, max_concurrent_trials=3
        ),
        search_space=dict(max_depth=dict(object="Sampler", type="Uniform", lower=1, upper=12)),
    )


@pytest.fixture
def example_result() -> Dict[str, Any]:
    return dict(
        object="BacktestResult",
        uuid="37faf8b5-5a4e-40e5-b90a-439a9743f921",
        create_time="2021-03-17T00:00:09Z",
        start_time="2021-03-17T00:00:10Z",
        end_time="2021-03-17T00:03:42Z",
        result_url="https://storage.cloud.google.com/backtest-result/37faf8b5-5a4e-40e5-b90a-439a9743f921.json",
        metrics=dict(mape=1.4, mae=43, rmse=1.39348),
    )


@pytest.fixture
def example_deployment(example_project: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Deployment",
        project=example_project["uuid"],
        uuid="3fa85f64-5717-4562-b3fc-2c963f66afa6",
        create_time="2021-01-01T01:23:45Z",
        title="My deployment",
        activate_time="2021-01-01T01:23:45Z",
        creator=example_project["creator"],
    )


@pytest.fixture
def example_hpo_result() -> Dict[str, Any]:
    return dict(
        data=[
            dict(
                object="HPOResult",
                uuid="37faf8b5-5a4e-40e5-b90a-439a9743f921",
                create_time="2021-03-17T00:00:09Z",
                metric="mse",
                best_trial=dict(parameters=dict(p1=3, p2=4), metrics=dict(mae=1.4, mse=43, rmse=1.39348)),
            )
        ],
        has_more=False,
    )


@pytest.fixture
def example_hpo_job(example_hpo: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="HPOJob",
        uuid="c72c0a3d-7690-4b22-bafb-267437a1e647",
        hpo=example_hpo["uuid"],
        state="SUCCESS",
        create_time="2021-03-17T00:00:09Z",
        schedule_time="2021-03-17T00:00:09Z",
        num_trials_completed=0,
    )
