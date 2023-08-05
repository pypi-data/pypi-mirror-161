from typing import TYPE_CHECKING, List, Union
from uuid import UUID

from myst.adapters.utils import get_resource_uuid
from myst.client import get_client
from myst.models.base_model import BaseModel
from myst.models.types import UUIDOrStr, to_uuid
from myst.openapi.api.projects.backtests.jobs import get_backtest_job, list_backtest_jobs
from myst.openapi.models.job_state import JobState

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.backtest import Backtest
    from myst.resources.project import Project


class BacktestJob(BaseModel):

    uuid: UUID
    backtest: UUID
    state: JobState

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], backtest: Union["Backtest", UUIDOrStr], uuid: UUIDOrStr
    ) -> "BacktestJob":
        """Gets a specific backtest job by its identifier."""
        backtest_job = get_backtest_job.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            backtest_uuid=str(get_resource_uuid(backtest)),
            uuid=str(to_uuid(uuid)),
        )

        return BacktestJob.parse_obj(backtest_job.dict())

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr], backtest: Union["Backtest", UUIDOrStr]) -> List["BacktestJob"]:
        """Lists all jobs for the backtest."""
        backtest_jobs = list_backtest_jobs.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            backtest_uuid=str(get_resource_uuid(backtest)),
        )

        return [BacktestJob.parse_obj(backtest_job) for backtest_job in backtest_jobs.data]

    def is_completed(self) -> bool:
        """Returns `True` if the job has completed.

        Completed jobs include both successful and failed jobs.

        Returns:
            whether the job has completed
        """
        return self.state in [JobState.SUCCESS, JobState.FAILURE]
