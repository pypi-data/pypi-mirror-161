import enum
from typing import Optional, Union
from uuid import UUID

from myst.connectors.model_connector import ModelConnector


@enum.unique
class GroupName(str, enum.Enum):
    FEATURES = "features"
    TARGETS = "targets"
    SAMPLE_WEIGHTS = "sample_weights"


@enum.unique
class RandomForestRegressionCriterion(str, enum.Enum):
    MSE = "mse"
    MAE = "mae"


class RandomForestRegression(ModelConnector):
    def __init__(
        self,
        n_estimators: Optional[int] = None,
        criterion: Optional[RandomForestRegressionCriterion] = None,
        max_depth: Optional[Optional[int]] = None,
        min_samples_split: Optional[Union[int, float]] = None,
        min_samples_leaf: Optional[Union[int, float]] = None,
        min_weight_fraction_leaf: Optional[float] = None,
        max_features: Optional[Optional[Union[int, float]]] = None,
        max_leaf_nodes: Optional[Optional[int]] = None,
        min_impurity_decrease: Optional[float] = None,
        bootstrap: Optional[bool] = None,
    ):
        super().__init__(
            uuid=UUID("b1d67b29-f60a-41f8-b15b-de9be74df160"),
            parameters=dict(
                n_estimators=n_estimators,
                criterion=criterion,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                min_weight_fraction_leaf=min_weight_fraction_leaf,
                max_features=max_features,
                max_leaf_nodes=max_leaf_nodes,
                min_impurity_decrease=min_impurity_decrease,
                bootstrap=bootstrap,
            ),
        )
