import time
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from myst.adapters.timing import to_timing_create
from myst.adapters.utils import drop_unset_values, get_resource_uuid
from myst.client import get_client
from myst.core.time.time import Time
from myst.models.base_model import BaseModel
from myst.models.timing import AbsoluteOrCronTiming, CronTiming, TimeRangeBoundary, from_time_range_boundary
from myst.models.types import UNSET, OptionalArgument, Unset, UUIDOrStr, to_uuid
from myst.openapi.api.projects.hpos import create_hpo, get_hpo, list_hpos, run_hpo, update_hpo
from myst.openapi.models.hpo_create import HPOCreate
from myst.openapi.models.hpo_job_state import HPOJobState
from myst.openapi.models.hpo_update import HPOUpdate
from myst.openapi.models.log_uniform import LogUniform as LogUniformModel
from myst.openapi.models.q_log_uniform import QLogUniform as QLogUniformModel
from myst.openapi.models.q_uniform import QUniform as QUniformModel
from myst.openapi.models.search_algorithm_create import SearchAlgorithmCreate
from myst.openapi.models.uniform import Uniform as UniformModel
from myst.resources.hpo_job import HPOJob
from myst.resources.hpo_result import HPOResult
from myst.resources.model import Model
from myst.resources.project import Project
from myst.resources.resource import Resource


class Uniform(BaseModel):
    lower: float
    upper: float


class QUniform(BaseModel):
    lower: float
    upper: float
    q: float


class LogUniform(BaseModel):
    lower: float
    upper: float
    base: Optional[int] = 10


class QLogUniform(BaseModel):
    lower: float
    upper: float
    q: float
    base: Optional[int] = 10


class Hyperopt(BaseModel):
    num_trials: Optional[int] = 10
    max_concurrent_trials: Optional[int] = 1


def _to_search_algorithm_create(hyper_opt: OptionalArgument[Hyperopt]) -> OptionalArgument[SearchAlgorithmCreate]:
    if isinstance(hyper_opt, Hyperopt):
        return SearchAlgorithmCreate(object="SearchAlgorithm", **hyper_opt.dict())
    else:
        return hyper_opt


def _to_search_space_create(
    search_space: OptionalArgument[Dict[str, Optional[Union[Uniform, QUniform, LogUniform, QLogUniform]]]]
) -> OptionalArgument[Dict[str, Optional[Union[UniformModel, QUniformModel, LogUniformModel, QLogUniformModel]]]]:
    if search_space is None:
        return None
    elif isinstance(search_space, Unset):
        return UNSET

    search_space_create: Dict[str, Optional[Union[UniformModel, QUniformModel, LogUniformModel, QLogUniformModel]]] = {}
    for key, value in search_space.items():
        if isinstance(value, Uniform):
            search_space_create[key] = UniformModel(object="Sampler", type="Uniform", **value.dict())
        elif isinstance(value, QUniform):
            search_space_create[key] = QUniformModel(object="Sampler", type="QUniform", **value.dict())
        elif isinstance(value, LogUniform):
            search_space_create[key] = LogUniformModel(object="Sampler", type="LogUniform", **value.dict())
        elif isinstance(value, QLogUniform):
            search_space_create[key] = QLogUniformModel(object="Sampler", type="QLogUniform", **value.dict())
        else:
            raise TypeError(
                "The `search_space` argument must be of type `Uniform`, `QUniform`, `LogUniform`, or `QLogUniform`."
            )

    return search_space_create


class HPO(Resource):

    title: str
    description: Optional[str]
    project: UUID
    model: UUID
    test_start_time: Time
    test_end_time: Time
    fit_start_timing: TimeRangeBoundary
    fit_end_timing: TimeRangeBoundary
    fit_reference_timing: AbsoluteOrCronTiming
    predict_start_timing: TimeRangeBoundary
    predict_end_timing: TimeRangeBoundary
    predict_reference_timing: CronTiming
    search_algorithm: Hyperopt
    search_space: Dict[str, Optional[Union[Uniform, QUniform, LogUniform, QLogUniform]]]

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        title: str,
        model: Union["Model", UUIDOrStr],
        test_start_time: Time,
        test_end_time: Time,
        fit_start_timing: TimeRangeBoundary,
        fit_end_timing: TimeRangeBoundary,
        fit_reference_timing: AbsoluteOrCronTiming,
        predict_start_timing: TimeRangeBoundary,
        predict_end_timing: TimeRangeBoundary,
        predict_reference_timing: CronTiming,
        search_algorithm: Hyperopt,
        search_space: Dict[str, Optional[Union[Uniform, QUniform, LogUniform, QLogUniform]]],
        description: Optional[str] = None,
    ) -> "HPO":
        """Creates a new HPO."""
        hpo = create_hpo.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            json_body=HPOCreate(
                object="HPO",
                title=title,
                description=description,
                model=str(get_resource_uuid(model)),
                test_start_time=test_start_time and test_start_time.to_iso_string() or None,
                test_end_time=test_end_time and test_end_time.to_iso_string() or None,
                fit_start_timing=to_timing_create(from_time_range_boundary(fit_start_timing)),
                fit_end_timing=to_timing_create(from_time_range_boundary(fit_end_timing)),
                fit_reference_timing=to_timing_create(fit_reference_timing),
                predict_start_timing=to_timing_create(from_time_range_boundary(predict_start_timing)),
                predict_end_timing=to_timing_create(from_time_range_boundary(predict_end_timing)),
                predict_reference_timing=to_timing_create(predict_reference_timing),
                search_algorithm=_to_search_algorithm_create(search_algorithm),
                search_space=_to_search_space_create(search_space),
            ),
        )
        return HPO.parse_obj(hpo.dict())

    @classmethod
    def get(cls, project: Union["Project", UUIDOrStr], uuid: UUIDOrStr) -> "HPO":
        """Gets a HPO by its identifier."""
        hpo = get_hpo.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project)), uuid=str(to_uuid(uuid))
        )

        return HPO.parse_obj(hpo.dict())

    def update(
        self,
        title: OptionalArgument[str] = UNSET,
        model: OptionalArgument[Union[Model, UUIDOrStr]] = UNSET,
        test_start_time: OptionalArgument[Time] = UNSET,
        test_end_time: OptionalArgument[Time] = UNSET,
        fit_start_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
        fit_end_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
        fit_reference_timing: OptionalArgument[AbsoluteOrCronTiming] = UNSET,
        predict_start_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
        predict_end_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
        predict_reference_timing: OptionalArgument[CronTiming] = UNSET,
        search_algorithm: OptionalArgument[Hyperopt] = UNSET,
        search_space: OptionalArgument[Dict[str, Optional[Union[Uniform, QUniform, LogUniform, QLogUniform]]]] = UNSET,
        description: OptionalArgument[str] = UNSET,
    ) -> "HPO":
        """Updates an HPO."""
        hpo_update: Dict[str, Any] = dict(
            object="HPO",
            title=title,
            description=description,
            model=str(get_resource_uuid(model)) if isinstance(model, Model) else model,
            test_start_time=test_start_time.to_iso_string() if isinstance(test_start_time, Time) else test_start_time,
            test_end_time=test_end_time.to_iso_string() if isinstance(test_end_time, Time) else test_end_time,
            fit_start_timing=to_timing_create(from_time_range_boundary(fit_start_timing)),
            fit_end_timing=to_timing_create(from_time_range_boundary(fit_end_timing)),
            fit_reference_timing=to_timing_create(fit_reference_timing),
            predict_start_timing=to_timing_create(from_time_range_boundary(predict_start_timing)),
            predict_end_timing=to_timing_create(from_time_range_boundary(predict_end_timing)),
            predict_reference_timing=to_timing_create(predict_reference_timing),
            search_algorithm=_to_search_algorithm_create(search_algorithm),
            search_space=_to_search_space_create(search_space),
        )

        hpo = update_hpo.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            uuid=str(self.uuid),
            json_body=HPOUpdate.parse_obj(drop_unset_values(hpo_update)),
        )

        return HPO.parse_obj(hpo.dict())

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr]) -> List["HPO"]:
        """Lists all HPOs associated with this project."""
        hpos = list_hpos.request_sync(client=get_client(), project_uuid=str(get_resource_uuid(project)))

        return [HPO.parse_obj(hpo) for hpo in hpos.data]

    @property
    def state(self) -> HPOJobState:
        """Returns the state of the HPO from the latest HPO job."""
        # Refresh the related job to get the most up to date state of the HPO.
        # Note that this will make a `get` request.
        return self.get_job().state

    def run(self) -> HPOJob:
        """Runs the HPO."""
        hpo_job = run_hpo.request_sync(client=get_client(), project_uuid=str(self.project), uuid=str(self.uuid))

        return HPOJob.parse_obj(hpo_job.dict())

    def get_job(self) -> HPOJob:
        """Gets the latest job associated with this HPO.

        Returns:
            the HPO job

        Raises:
            ValueError: if the job uuid cannot be inferred from a recent run
        """
        all_hpo_jobs = HPOJob.list(project=self.project, hpo=self)
        all_hpo_jobs.sort(key=lambda job: job.create_time, reverse=True)

        if len(all_hpo_jobs) == 0:
            raise ValueError("This HPO has not yet been `run`. Please run the HPO before requesting a job.")
        else:
            return all_hpo_jobs[0]

    def get_result(self) -> HPOResult:
        """Gets the latest result associated with a job for this HPO.

        Returns:
            the HPO result

        Raises:
            ValueError: if the job state is not `SUCCESS`
        """
        job = self.get_job()
        if job.state != "SUCCESS":
            raise (ValueError(f"Job state is `{job.state}`, should be `SUCCESS` to get result."))

        return HPOResult.get(project=self.project, hpo=self, job=job)

    def wait_until_completed(self) -> None:
        """Returns the hpo job once it has completed."""
        while True:
            refreshed_hpo_job = self.get_job()

            if refreshed_hpo_job.is_completed():
                break

            time.sleep(60)
