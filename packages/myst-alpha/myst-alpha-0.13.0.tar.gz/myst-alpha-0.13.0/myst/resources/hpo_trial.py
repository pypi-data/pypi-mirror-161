from typing import Any, Dict

import pandas as pd
from pydantic import BaseModel

from myst.openapi.models.hpo_metrics import HPOMetrics


class HPOTrial(BaseModel):
    parameters: Dict[str, Any]
    metrics: HPOMetrics

    def to_pandas_data_frame(self) -> pd.DataFrame:
        """Downloads the HPO result and converts the time arrays to pandas data frames.

        Data will be re-indexed against the predictions' natural time index, dropping any target data that doesn't
        correspond to a prediction.

        Returns:
            a pandas data frame with the predictions made by the HPO, and their corresponding targets. # noqa: DAR202

        Raises:
            NotImplementedError: currently is not implemented
        """
        raise NotImplementedError
