import base64
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID

import httpx

from myst.adapters.utils import get_resource_uuid
from myst.client import get_client
from myst.core.time.time import Time
from myst.models.time_dataset import TimeDataset
from myst.models.types import UUIDOrStr
from myst.openapi.api.projects.models.fit_results import get_model_fit_result, list_model_fit_results
from myst.openapi.api.projects.models.run_results import get_model_run_result, list_model_run_results
from myst.openapi.api.projects.time_series.run_results import get_time_series_run_result, list_time_series_run_results
from myst.resources.resource import Resource

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.model import Model
    from myst.resources.project import Project
    from myst.resources.time_series import TimeSeries


TENSORBOARD_FIT_STATE_KEY = "tensorboard_logs_base64"


class NodeResult(Resource):
    """Describes a result associated with a node.
    Attributes:
        project: the UUID of the project this result corresponds to
        node: the UUID of the node this result corresponds to
        start_time: the start time of this result
        end_time: the end time of this result
        as_of_time: the as of time of this result
    """

    project: UUID
    node: UUID
    start_time: Time
    end_time: Time
    as_of_time: Time


class ModelFitResult(NodeResult):
    """Results from a single run of a model fit.
    Attributes:
        fit_state_url: an external URL to the model fit state blob
    """

    fit_state_url: Optional[str]

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], model: Union["Model", UUIDOrStr], uuid: UUIDOrStr
    ) -> "ModelFitResult":
        """Gets a specific fit result by its identifier."""
        model_fit_result = get_model_fit_result.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            model_uuid=str(get_resource_uuid(model)),
            uuid=str(uuid),
        )

        return ModelFitResult.parse_obj(dict(model_fit_result.dict(), project=get_resource_uuid(project)))

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr], model: Union["Model", UUIDOrStr]) -> List["ModelFitResult"]:
        """Lists all fit results for the model."""
        model_fit_results = list_model_fit_results.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project)), model_uuid=str(get_resource_uuid(model))
        )

        return [
            ModelFitResult.parse_obj(dict(model_fit_result.dict(), project=get_resource_uuid(project)))
            for model_fit_result in model_fit_results.data
        ]

    def download_fit_state(self) -> Dict[str, Any]:
        """Downloads the fit state from the supplied URL and parses it."""
        # Lazy load the fit state URL, for example if this object was acquired through a list rather than a get.
        if self.fit_state_url is None:
            model_fit_result_detailed = get_model_fit_result.request_sync(
                client=get_client(), project_uuid=str(self.project), model_uuid=str(self.node), uuid=str(self.uuid)
            )
            self.fit_state_url = model_fit_result_detailed.fit_state_url

        response = httpx.get(self.fit_state_url)

        if response.status_code == 200:
            return json.loads(response.content)
        else:
            raise RuntimeError("Could not download fit state.")

    def download_tensorboard_logs(self, logs_dir: Union[Path, str] = "tensorboard_logs") -> None:
        """If available, downloads tensorboard logs for this model to the specified directory.

        Once you've downloaded tensorboard, you can view the logs with:

            $ tensorboard --logdir tensorboard_logs

        Note:
            - Log experiment names will be the model UUID
            - Log version names are formatted as "{fit start_time} – {fit end_time} ({fit as_of_time})"
            - This method supports downloading multiple tensorboard log experiment/versions to the same directory

        For example, if you run this method with `logs_dir` as "tensorboard_logs" on multiple model fit results across
        multiple models, you might see them show up in tensorboard with the organization:

            experiment / version
            -------------------------------
            model_uuid_1 / 2021-01-01T00:00:00Z – 2022-01-01T00:00:00Z (2022-06-01T00:00:00Z)
            model_uuid_1 / 2021-01-01T00:00:00Z – 2022-02-01T00:00:00Z (2022-06-01T00:00:00Z)
            model_uuid_2 / 2018-01-01T00:00:00Z – 2021-01-01T00:00:00Z (2022-06-02T00:00:00Z)

        Args:
            logs_dir: the top-level directory to download the logs to

        Raises:
            ValueError: if the fit state does not have associated tensorboard logs (key: "tensorboard_logs_base64")
        """
        fit_state = self.download_fit_state()
        if TENSORBOARD_FIT_STATE_KEY not in fit_state.keys():
            raise ValueError("This fit state does not contain tensorboard logs.")

        tensorboard_base64 = fit_state["tensorboard_logs_base64"]
        tensorboard_binary = base64.b64decode(tensorboard_base64)

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir = Path(tmp_dir_name)
            tmp_file = tmp_dir / "my_file.tar"
            with tmp_file.open("wb") as f:
                f.write(tensorboard_binary)
            shutil.unpack_archive(filename=tmp_file, extract_dir=os.path.join(logs_dir, str(self.node)), format="tar")


class ModelRunResultMetadata(NodeResult):
    """Describes the metadata of a result produced by a model run.
    This representation does not contain the inputs and outputs of a model run.
    """


class TimeSeriesRunResultMetadata(NodeResult):
    """Describes the metadata of a result produced by a time series run.
    This representation does not contain the outputs of a time series run.
    """


class ModelRunResult(ModelRunResultMetadata):
    """Describes a result produced by a model run.
    Attributes:
        inputs: inputs to the model run
        outputs: outputs of the model run
    """

    inputs: Dict[str, List[TimeDataset]]
    outputs: List[TimeDataset]

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], model: Union["Model", UUIDOrStr], uuid: UUIDOrStr
    ) -> "ModelRunResult":
        """Gets a specific run result by its identifier."""
        model_run_result = get_model_run_result.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            model_uuid=str(get_resource_uuid(model)),
            uuid=str(uuid),
        )

        return ModelRunResult.parse_obj(dict(model_run_result.dict(), project=get_resource_uuid(project)))

    @classmethod
    def list(
        cls, project: Union["Project", UUIDOrStr], model: Union["Model", UUIDOrStr]
    ) -> List[ModelRunResultMetadata]:
        """Lists all run results for the model."""
        model_run_results = list_model_run_results.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project)), model_uuid=str(get_resource_uuid(model))
        )

        return [
            ModelRunResultMetadata.parse_obj(dict(model_run_result.dict(), project=get_resource_uuid(project)))
            for model_run_result in model_run_results.data
        ]


class TimeSeriesRunResult(TimeSeriesRunResultMetadata):
    """Describes a result produced by a time series run.
    Attributes:
        outputs: outputs of the time series run
    """

    outputs: List[TimeDataset]

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], time_series: Union["TimeSeries", UUIDOrStr], uuid: UUIDOrStr
    ) -> "TimeSeriesRunResult":
        """Gets a specific run result by its identifier."""
        time_series_run_result = get_time_series_run_result.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            time_series_uuid=str(get_resource_uuid(time_series)),
            uuid=str(uuid),
        )

        return TimeSeriesRunResult.parse_obj(dict(time_series_run_result.dict(), project=get_resource_uuid(project)))

    @classmethod
    def list(
        cls, project: Union["Project", UUIDOrStr], time_series: Union["TimeSeries", UUIDOrStr]
    ) -> List[TimeSeriesRunResultMetadata]:
        """Lists all run results for the time series."""
        time_series_run_results = list_time_series_run_results.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            time_series_uuid=str(get_resource_uuid(time_series)),
        )

        return [
            TimeSeriesRunResultMetadata.parse_obj(
                dict(time_series_run_result.dict(), project=get_resource_uuid(project))
            )
            for time_series_run_result in time_series_run_results.data
        ]
