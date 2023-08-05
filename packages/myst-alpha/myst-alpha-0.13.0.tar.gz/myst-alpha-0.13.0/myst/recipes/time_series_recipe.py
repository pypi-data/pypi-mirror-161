from abc import ABC, abstractmethod
from typing import Optional, Union

from myst.models.types import UUIDOrStr
from myst.resources.project import Project
from myst.resources.time_series import TimeSeries


class TimeSeriesRecipe(ABC):
    """A recipe from which a time series can be created."""

    @abstractmethod
    def create(
        self, project: Union["Project", UUIDOrStr], title: Optional[str] = None, description: Optional[str] = None
    ) -> TimeSeries:
        """Creates and returns a new time series from this recipe in the given project.

        Args:
            project: the project in which to create the time series
            title: the title of the time series; if none is given, the recipe will supply a sensible default
            description: the description of the time series

        Returns:
            the created time series
        """
        raise NotImplementedError()
