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
class XGBoostObjective(str, enum.Enum):
    REG_SQUARED_ERROR = "reg:squarederror"
    BINARY_LOGISTIC = "binary:logistic"


class XGBoost(ModelConnector):
    def __init__(
        self,
        objective: Optional[XGBoostObjective] = None,
        num_boost_round: Optional[int] = None,
        max_depth: Optional[int] = None,
        min_child_weight: Optional[int] = None,
        learning_rate: Optional[float] = None,
        subsample: Optional[float] = None,
        colsample_bytree: Optional[float] = None,
        colsample_bylevel: Optional[float] = None,
        colsample_bynode: Optional[float] = None,
        gamma: Optional[float] = None,
        reg_alpha: Optional[float] = None,
        reg_lambda: Optional[float] = None,
        fit_on_null_values: Optional[bool] = None,
        predict_on_null_values: Optional[bool] = None,
    ) -> None:
        super().__init__(
            uuid=UUID("b78ff94a-27b1-4986-a88a-536661239bb2"),
            parameters=dict(
                colsample_bylevel=colsample_bylevel,
                colsample_bynode=colsample_bynode,
                colsample_bytree=colsample_bytree,
                fit_on_null_values=fit_on_null_values,
                gamma=gamma,
                learning_rate=learning_rate,
                max_depth=max_depth,
                min_child_weight=min_child_weight,
                num_boost_round=num_boost_round,
                objective=objective,
                predict_on_null_values=predict_on_null_values,
                reg_alpha=reg_alpha,
                reg_lambda=reg_lambda,
                subsample=subsample,
            ),
        )
