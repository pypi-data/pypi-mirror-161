# Myst Python Library

This is the official Python client library for the Myst Platform.

## Requirements

- Python 3.7+

## Installation

To install the package from PyPI:

    $ pip install --upgrade myst-alpha

## Authentication

The Myst API uses JSON Web Tokens (JWTs) to authenticate requests.

The Myst Python library handles the sending of JWTs to the API automatically and currently supports two ways to
authenticate to obtain a JWT: through your Google user account or a Myst service account.

### Authenticating using your user account

If you don't yet have a Google account, you can create one on the
[Google Account Signup](https://accounts.google.com/signup) page.

Once you have access to a Google account, send an email to `support@myst.ai` with your email so we can authorize you to
use the Myst Platform.

Use the following code snippet to authenticate using your user account:

```python
import myst

myst.authenticate()
```

The first time you run this, you'll be presented with a web browser and asked to authorize the Myst Python library to
make requests on behalf of your Google user account. If you'd like to re-authorize (for example with a different
account), pass `use_cache=False` to be presented with the web browser authorization once again.

### Authenticating using a service account

You can also authenticate using a Myst service account. To request a service account, email `support@myst.ai`.

To authenticate using a service account, set the `MYST_APPLICATION_CREDENTIALS` environment variable to the path to your
service account key file:

```sh
$ export MYST_APPLICATION_CREDENTIALS=</path/to/key/file.json>
```

Then, go through the service account authentication flow:

```python
import myst

myst.authenticate_with_service_account()
```

Alternatively, you can explicitly pass the path to your service account key:

```python
from pathlib import Path

import myst

myst.authenticate_with_service_account(key_file_path=Path("/path/to/key/file.json"))
```

## Connecting to a different environment

Contributors may want to connect to a non-production environment that they are authorized to develop in. In that case,
you can set the client with the API host you'd like to connect to.

```python
import myst

myst.set_client(myst.Client(api_host="https://petstore.api"))

myst.authenticate()
```

## Working with projects and graphs

A project is a workspace for setting up a graph of sources, models, operations, and time series to achieve a particular
objective. The sources, model, operations, and time series therein are _nodes_ of the graph, and they are connected by
different types of _edges_.

For more of a conceptual overview, see [the platform documentation](https://docs.myst.ai/docs). The following assumes
some familiarity with those concepts and focuses instead on demonstrating how to use the Myst client library to
interact with the platform.

### Projects

#### Create a project

```python
import myst

project = myst.Project.create(title="SF Electricity Load")
```

#### List projects

```python
import myst

projects = myst.Project.list()
```

#### Retrieve a project

```python
import myst

project = myst.Project.get(uuid="f89d7fbe-a051-4d0c-aa60-d6838b7e64a0")
```

#### Update a project

```python
import myst

project = myst.Project.get(uuid="f89d7fbe-a051-4d0c-aa60-d6838b7e64a0")
project = project.update(title="My Project")
```

### Nodes (Sources, Models, Operations, Time Series)

A node (source, model, operation, or time series) is always associated with a project, and there are multiple patterns
in the client library API by which you can list or create them.

#### Create a node

For example, suppose you want to create a temperature time series to be used as a feature in your model. Assuming that
you have the variable `project: Project` in scope, you can write the following to create a new time series:

```python
ksfo_temperature_time_series = project.create_time_series(
    title="Temperature (KSFO)",
    sample_period=myst.TimeDelta("PT1H"),  # Sample period of one hour. "PT1H" is an ISO 8601 duration string.
)
```

Or, to exactly the same effect:

```python
import myst

ksfo_temperature_time_series = myst.TimeSeries.create(
    project=project,  # Notice that project must be specified in this formulation.
    title="Temperature (KSFO)",
    sample_period=myst.TimeDelta("PT1H"),
)
```

This is true for the other types of nodes, too. In all, the client library offers the following equivalent ways to
create the different types of nodes:

- `project.create_source(...)` <=> `Source.create(project=project, ...)`
- `project.create_operation(...)` <=> `Operation.create(project=project, ...)`
- `project.create_model(...)` <=> `Model.create(project=project, ...)`
- `project.create_time_series(...)` <=> `TimeSeries.create(project=project, ...)`

#### Create a node with connector

For nodes that are powered by connectors, you must specify the parameters of that connector during construction. For
example, suppose you wanted to create a source node based on The Weather Company's Cleaned Observations API, to be used
as the source of temperature data in the time series we created above. To do so, you would write:

```python
from myst.connectors.source_connectors import cleaned_observations

ksfo_cleaned_observations = project.create_source(
    title="Cleaned Weather (KSFO)",
    connector=cleaned_observations.CleanedObservations(
        latitude=37.619,
        longitude=-122.374,
        fields=[
            cleaned_observations.Field.SURFACE_TEMPERATURE_CELSIUS,
        ],
    ),
)
```

`Model` and `Operation` nodes are constructed similarly. As another example, if we wanted to take the 3-hour rolling
mean of the temperature, we could create an operation as follows:

```python
import myst

from myst.connectors.operation_connectors import time_transformations

rolling_mean_ksfo_temperature = project.create_operation(
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
```

We will see how to connect an input to this operation [in a following step](#create-an-input).

#### List nodes in a project

```python
nodes = project.list_nodes()
```

#### Retrieve a node

```python
import myst

model = myst.Model.get(
    project="05703aea-7319-4623-810d-b92b58692906",
    uuid="a5ba722c-6750-4796-8b43-230b5e0f4c4a",
)
```

Similar for `myst.Source.get`, `myst.Operation.get`, and `myst.TimeSeries.get`.

#### Update a node

```python
import myst

model = myst.Model.get(
    project="05703aea-7319-4623-810d-b92b58692906",
    uuid="a5ba722c-6750-4796-8b43-230b5e0f4c4a",
)
model = model.update(title="My Model")
```

Similar for updating `Source`, `Operation`, and `TimeSeries` instances.

### Edges (Inputs, Layers)

#### Create a layer

A layer is an edge that feeds into a time series. You can create a layer into a time series with either:

```python
import myst
from myst.connectors.source_connectors import cleaned_observations

layer = ksfo_temperature_time_series.create_layer(
    node=ksfo_cleaned_observations,
    order=0,
    end_timing=myst.TimeDelta("-PT23H"),
    label_indexer=cleaned_observations.Field.SURFACE_TEMPERATURE_CELSIUS.value,
)
```

or:

```python
import myst
from myst.connectors.source_connectors import cleaned_observations

layer = myst.Layer.create(
    time_series=ksfo_temperature_time_series,
    node=ksfo_cleaned_observations,
    order=0,
    end_timing=myst.TimeDelta("-PT23H"),
    label_indexer=cleaned_observations.Field.SURFACE_TEMPERATURE_CELSIUS.value,
)
```

#### Update a layer

```python
import myst

layer = myst.Layer.get(
    project="05703aea-7319-4623-810d-b92b58692906",
    uuid="a5ba722c-6750-4796-8b43-230b5e0f4c4a",
)
layer = layer.update(order=2)
```

#### Create an input

An input is an edge that feeds into a model or an operation. To connect the temperature time series into the operation
we constructed before, we would write:

```python
from myst.connectors.operation_connectors import time_transformations

operation_input = rolling_mean_ksfo_temperature.create_input(
    time_series=ksfo_temperature_time_series,
    group_name=time_transformations.GroupName.OPERANDS,
)
```

As always, this creation method is also available as:

```python
import myst

from myst.connectors.operation_connectors import time_transformations


operation_input = myst.Input.create(
    time_series=rolling_mean_ksfo_temperature,
    node=ksfo_temperature_time_series,
    group_name=time_transformations.GroupName.OPERANDS,
)
```

#### Update an input

```python
import myst

input_ = myst.Input.get(
    project="05703aea-7319-4623-810d-b92b58692906",
    uuid="a5ba722c-6750-4796-8b43-230b5e0f4c4a",
)
input_ = input_.update(group_name="My Group Name")
```

#### List time series layers

```python
layers = ksfo_temperature_time_series.list_layers()
```

#### List model/operation inputs

```python
inputs = rolling_mean_ksfo_temperature.list_inputs()
```

## Working with time series

Time series are at the core of Myst's API. In addition to the functionality offered by a generic node, time series also
support querying and inserting data.

First, retrieve a time series:

```python
import myst

time_series = myst.TimeSeries.get(
    project="40bcb171-1c51-4497-9524-914630818aeb",
    uuid="ca2a63d1-3515-47b4-afc7-13c6656dd744",
)
```

To insert a `TimeArray` of random scalar data into the time series:

```python
import myst
import numpy as np

time_array = myst.TimeArray(
    sample_period="PT1H",
    start_time="2021-07-01T00:00:00Z",
    end_time="2021-07-08T00:00:00Z",
    as_of_time="2021-07-01T00:00:00Z",
    values=np.random.randn(168),
)
time_series.insert_time_array(time_array=time_array)
```

You can also query a time series for a given as of time and natural time range. In this example, the query will return
the data we just inserted:

```python
import myst

returned_time_array = time_series.query_time_array(
    start_time=myst.Time("2021-07-01T00:00:00Z"),
    end_time=myst.Time("2021-07-08T00:00:00Z"),
    as_of_time=myst.Time("2021-07-01T00:00:00Z"),
)
assert returned_time_array == time_array
```

You are also able to update a time series

```python
import myst

time_series = myst.TimeSeries.get(
    project="40bcb171-1c51-4497-9524-914630818aeb",
    uuid="ca2a63d1-3515-47b4-afc7-13c6656dd744",
)
time_series = time_series.update(title="My Time Series")
```

## Working with policies

A policy is the way to specify the schedule on which a particular target will be fit or run, as well as the parameters
around the target time range.

At the time of this writing, the Myst Platform supports two types of policies: _time series run policies_ and _model fit
policies_.

### Time series run policies

#### Create a time series run policy

```python
import myst

ksfo_temp_run_policy = ksfo_temperature_time_series.create_run_policy(
    schedule_timing=myst.TimeDelta("PT1H"),  # Run every hour.
    start_timing=myst.TimeDelta("PT1H"),  # Run on data starting from an hour from now (inclusive)...
    end_timing=myst.TimeDelta("P7D"),  # ...up to 7 days from now (exclusive).
)
```

#### Update a time series run policy

```python
import myst

time_series_run_policy = myst.TimeSeriesRunPolicy.get(
    project="05703aea-7319-4623-810d-b92b58692906",
    uuid="a5ba722c-6750-4796-8b43-230b5e0f4c4a",
)
time_series_run_policy = time_series_run_policy.update(active=False)
```

### Model fit policies

Suppose we have a variable `xgboost_model` that contains a value of type `Model`.

#### Create a model fit policy

```python
import myst

xgboost_model_fit_policy = xgboost_model.create_fit_policy(
    schedule_timing=myst.TimeDelta("PT24H"),  # Run every 24 hours.
    start_timing=myst.Time("2021-01-01T00:00:00Z"),  # Fit on data from the beginning of 2021 (UTC)...
    end_timing=myst.TimeDelta("-PT1H"),  # ...up to an hour ago (exclusive).
)
```

#### Update a model fit policy

```python
import myst

model_fit_policy = myst.ModelFitPolicy.get(
    project="05703aea-7319-4623-810d-b92b58692906",
    uuid="a5ba722c-6750-4796-8b43-230b5e0f4c4a",
)
model_fit_policy = model_fit_policy.update(active=False)
```

## Deploying

In order for the graph to be executed, it must first be _deployed_. The Python client library does not currently support
this functionality; we recommend using the Myst Platform UI to deploy a project.

## Backtesting

In order to run a backtest, make sure that you have created and deployed a project and graph with a model you want to backtest.

### Listing backtests

```python
import myst

# Use an existing project.
project = myst.Project.get(uuid="<uuid>")

# List all backtests associated with the project.
backtests = myst.Backtest.list(project=project)
```

### Creating and running backtest

```python
import myst

# Use an existing project.
project = myst.Project.get(uuid="<uuid>")

# Use an existing deployed model within the project.
model = myst.Model.get(project=project, uuid="<uuid>")

# Create a backtest.
backtest = myst.Backtest.create(
    project=project,
    title="My Backtest",
    model=model,
    test_start_time=myst.Time("2021-07-01T00:00:00Z"),
    test_end_time=myst.Time("2022-01-01T00:00:00Z"),
    fit_start_timing=myst.TimeDelta("-P1M"),
    fit_end_timing=myst.TimeDelta("-PT24H"),
    fit_reference_timing=myst.CronTiming(cron_expression="0 0 * * 1"),
    predict_start_timing=myst.TimeDelta("PT1H"),
    predict_end_timing=myst.TimeDelta("PT24H"),
    predict_reference_timing=myst.CronTiming(cron_expression="0 0 * * *"),
)

# Run the backtest.
backtest.run()
```

### Analyze backtest results

To extract the result of a backtest in the client library, you can use the following code:

```python
import myst

# Use an existing project.
project = myst.Project.get(uuid="<uuid>")

# Use an existing backtest within the project.
backtest = myst.Backtest.get(project=project, uuid="<uuid>")

# Wait until the backtest is complete.
backtest.wait_until_completed()

# Get the result of the completed backtest.
backtest_result = backtest.get_result()
```

Once you have extracted your backtest result, you can use the following code to generate metrics:

```python
# Get `mape`, `mae`, and `rmse` from the result object.
metrics_dictionary = backtest_result.metrics

# To calculate custom metrics, map the backtest result to a pandas data frame.
result_data_frame = backtest_result.to_pandas_data_frame()

# Compute some metrics for the backtest result.
absolute_error_series = (result_data_frame["targets"] - result_data_frame["predictions"]).abs()
absolute_percentage_error_series = absolute_error_series / result_data_frame["targets"].abs()

# Create an index with the prediction horizons.
horizon_index = (
    result_data_frame.index.get_level_values("time") -
    result_data_frame.index.get_level_values("reference_time")
)

# Print the MAE and MAPE for each prediction horizon.
print(absolute_error_series.groupby(horizon_index).mean())
print(absolute_percentage_error_series.groupby(horizon_index).mean())
```

### update a backtest

```python
import myst

backtest = myst.Backtest.get(
    project="05703aea-7319-4623-810d-b92b58692906",
    uuid="a5ba722c-6750-4796-8b43-230b5e0f4c4a",
)
backtest = backtest.update(title="My backtest")
```

## HPO

In order to run an HPO, make sure that you have created a project and graph with a model you want to optimize.

### Listing HPOs

```python
import myst

# Use an existing project.
project = myst.Project.get(uuid="<uuid>")

# List all HPOs associated with the project.
hpos = myst.HPO.list(project=project)
```

### Creating and running HPO

```python
import myst

# Use an existing project.
project = myst.Project.get(uuid="<uuid>")

# Use an existing deployed model within the project.
model = myst.Model.get(project=project, uuid="<uuid>")

# Create an hpo.
hpo = myst.HPO.create(
    project=project,
    title="My HPO",
    model=model,
    search_space={
        "num_boost_round": myst.hpo.LogUniform(lower=100, upper=1000),
        "max_depth": myst.hpo.QUniform(lower=1, upper=12, q=1),
        "learning_rate": myst.hpo.LogUniform(lower=0.005, upper=0.2),
        "min_child_weight": myst.hpo.QUniform(lower=0, upper=100, q=5),
    },
    search_algorithm=myst.hpo.Hyperopt(num_trials=10, max_concurrent_trials=5),
    test_start_time=myst.Time("2021-07-01T00:00:00Z"),
    test_end_time=myst.Time("2022-01-01T00:00:00Z"),
    fit_start_timing=myst.TimeDelta("-P1M"),
    fit_end_timing=myst.TimeDelta("-PT24H"),
    fit_reference_timing=myst.CronTiming(cron_expression="0 0 * * 1"),
    predict_start_timing=myst.TimeDelta("PT1H"),
    predict_end_timing=myst.TimeDelta("PT24H"),
    predict_reference_timing=myst.CronTiming(cron_expression="0 0 * * *"),
)

# Run the HPO.
hpo.run()
```

### Analyze HPO results

To extract the result of an HPO in the client library, you can use the following code:

```python
import myst

# Use an existing project.
project = myst.Project.get(uuid="<uuid>")

# Use an existing HPO within the project.
hpo = myst.HPO.get(project=project, uuid="<uuid>")

# Wait until the HPO is complete.
hpo.wait_until_completed()

# Get the result of the completed HPO.
hpo_result = hpo.get_result()
```

Once you have extracted your HPO result, you can use the following code to get the optimize parameters
and the metrics from the best_trial:

```python
# Get the optimized parameters for the best trial.
parameters = hpo_result.best_trial.parameters

# Get the pre-computed metrics for the best trial.
metrics = hpo_result.best_trial.metrics
```

### update an HPO

```python
import myst

hpo = myst.HPO.get(
    project="05703aea-7319-4623-810d-b92b58692906",
    uuid="a5ba722c-6750-4796-8b43-230b5e0f4c4a",
)
hpo = hpo.update(title="My HPO")
```

## Further Examples

For more full-featured usage examples of the Myst Platform Python client library, see the
`/examples` folder.

## Support

For questions or just to say hi, reach out to `support@myst.ai`.
