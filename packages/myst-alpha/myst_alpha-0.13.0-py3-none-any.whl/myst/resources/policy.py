from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID

from myst import Time, TimeDelta
from myst.adapters.timing import to_timing_create
from myst.adapters.utils import UNSET, drop_unset_values, get_resource_uuid
from myst.client import get_client
from myst.models.timing import (
    AbsoluteOrRelativeTiming,
    ScheduleTiming,
    TimeRangeBoundary,
    from_schedule_specifier,
    from_time_range_boundary,
)
from myst.models.types import OptionalArgument, UUIDOrStr
from myst.openapi.api.projects.models.fit_policies import (
    create_model_fit_policy,
    get_model_fit_policy,
    list_model_fit_policies,
    update_model_fit_policy,
)
from myst.openapi.api.projects.time_series.run_policies import (
    create_time_series_run_policy,
    get_time_series_run_policy,
    list_time_series_run_policies,
    update_time_series_run_policy,
)
from myst.openapi.models.model_fit_policy_create import ModelFitPolicyCreate
from myst.openapi.models.model_fit_policy_update import ModelFitPolicyUpdate
from myst.openapi.models.time_series_run_policy_create import TimeSeriesRunPolicyCreate
from myst.openapi.models.time_series_run_policy_update import TimeSeriesRunPolicyUpdate
from myst.resources.resource import Resource

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.model import Model
    from myst.resources.project import Project
    from myst.resources.time_series import TimeSeries


class Policy(Resource):
    """Describes when and over what natural time range to run a particular type of job for a node.

    Attributes:
        project: the identifier of the project this policy belongs to
        creator: the identifier of the user who created this resource
        schedule_timing: when the policy is scheduled to run, whether recurrent or once
        active: whether this policy is currently in effect
        node: the identifier of the node this policy applies to
        start_timing: the beginning of the natural time range for which this policy applies, inclusive
        end_timing: the end of the natural time range for which this policy applies, exclusive
    """

    project: UUID
    creator: UUID
    schedule_timing: ScheduleTiming
    active: bool
    node: UUID
    start_timing: AbsoluteOrRelativeTiming
    end_timing: AbsoluteOrRelativeTiming


class ModelFitPolicy(Policy):
    """Describes when and over what natural time range to run a fit job on a model."""

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        model: Union["Model", UUIDOrStr],
        schedule_timing: Union[Time, TimeDelta, ScheduleTiming],
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
        active: bool = True,
    ) -> "ModelFitPolicy":
        """Creates a fit policy for the model."""
        model_fit_policy_create = ModelFitPolicyCreate(
            object="Policy",
            type="ModelFitPolicy",
            schedule_timing=to_timing_create(from_schedule_specifier(schedule_timing)),
            start_timing=to_timing_create(from_time_range_boundary(start_timing)),
            end_timing=to_timing_create(from_time_range_boundary(end_timing)),
            active=active,
        )

        model_fit_policy = create_model_fit_policy.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            model_uuid=str(get_resource_uuid(model)),
            json_body=model_fit_policy_create,
        )

        return ModelFitPolicy.parse_obj(dict(model_fit_policy.dict(), project=get_resource_uuid(project)))

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], model: Union["Model", UUIDOrStr], uuid: UUIDOrStr
    ) -> "ModelFitPolicy":
        """Gets a specific fit policy by its identifier."""
        model_fit_policy = get_model_fit_policy.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            model_uuid=str(get_resource_uuid(model)),
            uuid=str(uuid),
        )

        return ModelFitPolicy.parse_obj(dict(model_fit_policy.dict(), project=get_resource_uuid(project)))

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr], model: Union["Model", UUIDOrStr]) -> List["ModelFitPolicy"]:
        """Lists all fit policies for the model."""
        model_fit_policies = list_model_fit_policies.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project)), model_uuid=str(get_resource_uuid(model))
        )

        return [
            ModelFitPolicy.parse_obj(dict(model_fit_policy.dict(), project=get_resource_uuid(project)))
            for model_fit_policy in model_fit_policies.data
        ]

    def update(
        self,
        schedule_timing: OptionalArgument[Union[Time, TimeDelta, ScheduleTiming]] = UNSET,
        start_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
        end_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
        active: OptionalArgument[bool] = UNSET,
    ) -> "ModelFitPolicy":
        """Updates the fit policy for the model."""
        model_fit_policy_update: Dict[str, Any] = dict(
            object="Policy",
            type="ModelFitPolicy",
            schedule_timing=to_timing_create(from_schedule_specifier(schedule_timing)),
            start_timing=to_timing_create(from_time_range_boundary(start_timing)),
            end_timing=to_timing_create(from_time_range_boundary(end_timing)),
            active=active,
        )

        model_fit_policy = update_model_fit_policy.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            model_uuid=str(self.node),
            uuid=str(self.uuid),
            json_body=ModelFitPolicyUpdate.parse_obj(drop_unset_values(model_fit_policy_update)),
        )

        return ModelFitPolicy.parse_obj(dict(model_fit_policy.dict(), project=self.project))


class TimeSeriesRunPolicy(Policy):
    """Describes when and over what natural time range to run a fit job on a model."""

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        time_series: Union["TimeSeries", UUIDOrStr],
        schedule_timing: Union[Time, TimeDelta, ScheduleTiming],
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
        active: bool = True,
    ) -> "TimeSeriesRunPolicy":
        """Creates a run policy for the time series."""
        time_series_run_policy_create = TimeSeriesRunPolicyCreate(
            object="Policy",
            type="TimeSeriesRunPolicy",
            schedule_timing=to_timing_create(from_schedule_specifier(schedule_timing)),
            start_timing=to_timing_create(from_time_range_boundary(start_timing)),
            end_timing=to_timing_create(from_time_range_boundary(end_timing)),
            active=active,
        )

        time_series_run_policy = create_time_series_run_policy.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            time_series_uuid=str(get_resource_uuid(time_series)),
            json_body=time_series_run_policy_create,
        )

        return TimeSeriesRunPolicy.parse_obj(dict(time_series_run_policy.dict(), project=get_resource_uuid(project)))

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], time_series: Union["TimeSeries", UUIDOrStr], uuid: UUIDOrStr
    ) -> "TimeSeriesRunPolicy":
        """Gets a specific run policy by its identifier."""
        time_series_run_policy = get_time_series_run_policy.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            time_series_uuid=str(get_resource_uuid(time_series)),
            uuid=str(uuid),
        )

        return TimeSeriesRunPolicy.parse_obj(dict(time_series_run_policy.dict(), project=get_resource_uuid(project)))

    @classmethod
    def list(
        cls, project: Union["Project", UUIDOrStr], time_series: Union["TimeSeries", UUIDOrStr]
    ) -> List["TimeSeriesRunPolicy"]:
        """Lists all run policies for the time series."""
        time_series_run_policies = list_time_series_run_policies.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            time_series_uuid=str(get_resource_uuid(time_series)),
        )

        return [
            TimeSeriesRunPolicy.parse_obj(dict(time_series_run_policy.dict(), project=get_resource_uuid(project)))
            for time_series_run_policy in time_series_run_policies.data
        ]

    def update(
        self,
        schedule_timing: OptionalArgument[Union[Time, TimeDelta, ScheduleTiming]] = UNSET,
        start_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
        end_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
        active: OptionalArgument[bool] = UNSET,
    ) -> "TimeSeriesRunPolicy":
        """Updates the run policy for the time series."""
        time_series_run_policy_update: Dict[str, Any] = dict(
            object="Policy",
            type="TimeSeriesRunPolicy",
            schedule_timing=to_timing_create(from_schedule_specifier(schedule_timing)),
            start_timing=to_timing_create(from_time_range_boundary(start_timing)),
            end_timing=to_timing_create(from_time_range_boundary(end_timing)),
            active=active,
        )

        time_series_run_policy = update_time_series_run_policy.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            time_series_uuid=str(self.node),
            uuid=str(self.uuid),
            json_body=TimeSeriesRunPolicyUpdate.parse_obj(drop_unset_values(time_series_run_policy_update)),
        )

        return TimeSeriesRunPolicy.parse_obj(dict(time_series_run_policy.dict(), project=self.project))
