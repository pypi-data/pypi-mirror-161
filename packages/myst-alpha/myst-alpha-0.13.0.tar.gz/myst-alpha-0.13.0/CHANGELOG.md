# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# `myst-alpha` package

The following release notes pertain to the `myst-alpha` package, where development is ongoing while the API is unstable.

## [0.13.0](https://pypi.org/project/myst-alpha/0.13.0) - 2022-07-28

### Added

- Distribution Operation Connectors

## [0.12.0](https://pypi.org/project/myst-alpha/0.12.0) - 2022-07-21

### Added

- NGBoost Model Connector

### Changed

- Add remaining CRUD methods for core resources
- Split `Input` into `ModelInput` and `OperationInput`
- Rename `Layer` to `TimeSeriesLayer`
- Get methods now accept identifiers or objects

## [0.11.1](https://pypi.org/project/myst-alpha/0.11.1) - 2022-07-07

### Fixed

- Bug that was causing import to fail

## [0.11.0](https://pypi.org/project/myst-alpha/0.11.0) - 2022-07-07

### Added

- Hyperparameter Optimization (HPO)
- Binary objectives for XGBoost and LightGBM models

## [0.10.0](https://pypi.org/project/myst-alpha/0.10.0) - 2022-06-17

### Changed

- Faster tensorboard downloads.

## [0.9.0](https://pypi.org/project/myst-alpha/0.9.0) - 2022-05-12

### Changed

- YesEnergy connector removed previously-required `username` and `password` fields.

## [0.8.4](https://pypi.org/project/myst-alpha/0.8.4) - 2022-04-22

### Added

- The TWC recipes now accepts a `create_intermediate_time_series`, which determines whether an optional intermediate time series should be created with one layer for each source.

## [0.8.3](https://pypi.org/project/myst-alpha/0.8.3/) - 2022-04-07

### Added

- MLPRegression Model Connector
- FillNA Operation Connector

## [0.8.2](https://pypi.org/project/myst-alpha/0.8.2/) - 2022-03-31

### Added

- Enables TWC recipes to accept a latitude / longitude as inputs as well as metar stations
- Backtest list

## [0.8.1](https://pypi.org/project/myst-alpha/0.8.1/) - 2022-03-24

### Changed

- Adds support to the TWC time series recipe for the following fields: Cloud Coverage, Dew Point Temperature, and Wind Chill Temperature.
- Adds the `fit_on_null_values` and `predict_on_null_values` parameters to the atrus XGBoost model connector.

## [0.8.0](https://pypi.org/project/myst-alpha/0.8.0/) - 2022-03-21

### Changed

- Changed Cleaned Observations connector field name from `windSpeedMph` to `windSpeedKph`

## [0.7.0](https://pypi.org/project/myst-alpha/0.7.0/) - 2022-03-17

### Added

- Added ability to deploy a project.
- Added new connectors:
  - `ExtraTreesRegression`
  - `ElasticNet`

### Changed

- Users can now specify `CronTiming` as the `schedule_timing` in policies.

### Removed

- Removed duplicate `CronTiming` implementation.

## [0.6.0](https://pypi.org/project/myst-alpha/0.6.0/) - 2022-03-14

### Added

- Ability to share project on create.
- Added back the `LinearRegression` connector and added a `RandomForestRegression` connector.
- Added dummy operator.

## [0.5.0](https://pypi.org/project/myst-alpha/0.5.0/) - 2022-02-17

### Added

- Added the LightGBM connector.
- Metrics are now available on backtest results.

### Fixed

- Fixed a bug causing some `MystClientError`s to be incorrectly raised as `pydantic.ValidationError`s.

### Removed

- Removed the linear regression connector.

## [0.4.1](https://pypi.org/project/myst-alpha/0.4.1/) - 2022-01-31

### Added

- Core [Backtesting](https://docs.myst.ai/docs/backtesting) functionality, including:
  - Create, get, and run a backtest
  - Monitor a running backtest using `backtest.state` and `backtest.wait_until_completed()`
  - Get a backtest result and convert it to a pandas data frame

### Changed

- Improved authorization to automatically refresh tokens.
- Error messages now distinguish between issues that are `Not found (404)` and `Unauthorized (403)`. For example, the Platform will now raise an `Unauthorized (403)` error if your project is shared with only `viewer` access but requires `editor` access.

## [0.4.0](https://pypi.org/project/myst-alpha/0.4.0/) - 2022-01-03

### Changed

- Retrieving nodes now requires a project identifier.

## [0.3.1](https://pypi.org/project/myst-alpha/0.3.1/) - 2021-12-08

### Added

- Resampling connector

## [0.3.0](https://pypi.org/project/myst-alpha/0.3.0/) - 2021-12-07

### Added

- Abstract time series recipe definition and concrete recipe for The Weather Company time series

## [0.2.3](https://pypi.org/project/myst-alpha/0.2.3/) - 2021-11-19

### Added

- Model fit result list, get, download fit state
- Query time series data by as of offset

## [0.2.2](https://pypi.org/project/myst-alpha/0.2.2/) - 2021-10-06

### Changed

- OpenAPI models now ignore rather than forbid new fields added to the API.

## [0.2.1](https://pypi.org/project/myst-alpha/0.2.1/) - 2021-09-23

### Added

- Time series run policy create, list
- Model fit policy create, list

## [0.2.0](https://pypi.org/project/myst-alpha/0.2.0/) - 2021-09-17

### Added

- Core graph creation functionality, including:
  - Project create, list, get
  - List project nodes, list project edges
  - Source create, get
  - Model create, get
  - Operation create, get
  - Time series create
  - Input create, list {source, model, operation} inputs
  - Layer create, list time series layers
- Parameters and identifiers of Myst-provided connectors defined

### Changed

- Start timing/end timing of layers can be specified with `Time` and `TimeDelta` objects
- `AbsoluteTiming`, `RelativeTiming` now visible from `myst` module

## [0.1.3](https://pypi.org/project/myst-alpha/0.1.3/) - 2021-09-10

### Changed

- Loosened version restrictions on several dependencies.
- Service account authentication has correct audience specified.
- Dependency on numpy.typing module removed.

## [0.1.2](https://pypi.org/project/myst-alpha/0.1.2/) - 2021-09-02

### Changed

- API host is now configurable via `myst.settings.MYST_API_HOST`.
- Bugfix: Validation errors (HTTP 422) handled properly.
- Bugfix: Specifying the environment variable `MYST_APPLICATION_CREDENTIALS` no longer causes `import myst` to fail.
- Bugfix: Don't assume that the directory `~/.config` already exists.

### Added

- Added py.typed file per PEP 561.

## [0.1.1](https://pypi.org/project/myst-alpha/0.1.1/) - 2021-08-16

### Changed

- Default API host set to production instance rather than dev.

## [0.1.0](https://pypi.org/project/myst-alpha/0.1.0/) - 2021-08-12

### Changed

- Client handwritten rather than auto-generated.
- Only non-auth methods are `TimeSeries.get`, `TimeSeries.query_time_array`, and `TimeSeries.insert_time_array`.

## [0.0.1](https://pypi.org/project/myst-alpha/0.0.1/) - 2021-07-09

### Added

- New API routes and endpoints for deletion
- API routes and endpoints for policies and project results

### Changed

- Re-factored client generation to be compatible with python packaging

This is the initial `myst-alpha` release.

### Added

- Authentication via Google credentials
- Interact with [Myst's](https://myst.ai) `v1alpha2` API via auto-generated OpenAPI client
- Initial (concealed) CLI via `typer`
- Tested using `pytest` and matrix tests via Github Actions

# `myst` package

Prior to the interim period of development of the `myst-alpha` project, releases were under `myst` (and will be again).

## [1.0.4](https://pypi.org/project/myst/1.0.4/) - 2020-12-01

### Added

- Switched to using soft dependency matching in `requirements.txt` to play nicely with `pip` version 20.3's (see
  [`pip` changelog](https://pip.pypa.io/en/stable/news/) for details) new strict dependency resolution.

## [1.0.3](https://pypi.org/project/myst/1.0.3/) - 2020-08-27

### Added

- Improved authentication logic that only refreshes Google OAuth credentials when they expire, which reduces
  authentication rate limiting.

## [1.0.2](https://pypi.org/project/myst/1.0.2/) - 2020-03-30

### Added

- Improved retry logic that retries native Python errors, including network-related errors like `ConnectionError`.

### Changed

- Upgraded `google-auth` dependency to version 1.11.0.

## [1.0.1](https://pypi.org/project/myst/1.0.1/) - 2020-01-06

### Added

- Basic retry logic.
- Support for passing the `service_account_key_file_path` to `myst.authenticate` without having to also specify the `use_service_account` flag.

### Changed

- Renamed `TimeSeries.fetch_data` to `TimeSeries.fetch_data_series`.

## [1.0.0](https://pypi.org/project/myst/1.0.0/) - 2020-01-06 [YANKED]

### Added

- Basic retry logic.
- Support for passing the `service_account_key_file_path` to `myst.authenticate` without having to also specify the `use_service_account` flag.

## [0.1.1](https://pypi.org/project/myst/0.1.1/) - 2019-09-17

### Added

- First official `myst` release
- Support for authenticating using a Google User Account
- Support for authenticating with a Myst AI Service Account
- Support for listing, getting, and fetching data for `TimeSeries`
- Support for caching and clearing credentials locally

## [0.0.1](https://pypi.org/project/myst/0.0.1/) - 2019-05-01

### Added

- Initial empty `myst` release
