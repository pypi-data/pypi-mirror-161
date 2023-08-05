import enum
from typing import Optional
from uuid import UUID

from myst.connectors.model_connector import ModelConnector


@enum.unique
class GroupName(str, enum.Enum):
    FEATURES = "features"
    TARGETS = "targets"
    SAMPLE_WEIGHTS = "sample_weights"


@enum.unique
class LightGBMObjective(str, enum.Enum):
    BINARY = "binary"
    MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
    MEAN_ABSOLUTE_PERCENTAGE_ERROR = "mean_absolute_percentage_error"
    MEAN_SQUARED_ERROR = "mean_squared_error"
    QUANTILE = "quantile"


class LightGBM(ModelConnector):
    def __init__(
        self,
        objective: Optional[LightGBMObjective] = None,
        num_boost_round: Optional[int] = None,
        max_depth: Optional[int] = None,
        min_child_weight: Optional[int] = None,
        learning_rate: Optional[float] = None,
        subsample: Optional[float] = None,
        colsample_bytree: Optional[float] = None,
        colsample_bynode: Optional[float] = None,
        max_leaves: Optional[int] = None,
        min_data_in_leaf: Optional[int] = None,
        min_gain_to_split: Optional[float] = None,
        alpha: Optional[float] = None,
        reg_alpha: Optional[float] = None,
        reg_lambda: Optional[float] = None,
        fit_on_null_values: Optional[bool] = None,
        predict_on_null_values: Optional[bool] = None,
    ) -> None:
        super().__init__(
            uuid=UUID("629da569-9d4a-4011-b27a-30c72f0ca1dc"),
            parameters=dict(
                objective=objective,
                num_boost_round=num_boost_round,
                max_depth=max_depth,
                min_child_weight=min_child_weight,
                learning_rate=learning_rate,
                subsample=subsample,
                colsample_bytree=colsample_bytree,
                colsample_bynode=colsample_bynode,
                max_leaves=max_leaves,
                min_data_in_leaf=min_data_in_leaf,
                min_gain_to_split=min_gain_to_split,
                alpha=alpha,
                reg_alpha=reg_alpha,
                reg_lambda=reg_lambda,
                fit_on_null_values=fit_on_null_values,
                predict_on_null_values=predict_on_null_values,
            ),
        )
