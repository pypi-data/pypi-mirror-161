import enum
from typing import Optional, Tuple
from uuid import UUID

from myst.connectors.model_connector import ModelConnector


@enum.unique
class GroupName(str, enum.Enum):
    CATEGORICAL_FEATURES = "categorical_features"
    CONTINUOUS_FEATURES = "continuous_features"
    TARGETS = "targets"
    SAMPLE_WEIGHTS = "sample_weights"


@enum.unique
class RegressionLossFunction(str, enum.Enum):
    RMSE = "rmse"
    MAE = "mae"


class MLPRegression(ModelConnector):
    def __init__(
        self,
        batch_size: Optional[int] = None,
        max_training_epochs: Optional[int] = None,
        min_relative_loss_change: Optional[float] = None,
        patience: Optional[int] = None,
        embedding_dimension: Optional[int] = None,
        hidden_layer_dimensions: Optional[Tuple[int, ...]] = None,
        dropout_rate: Optional[float] = None,
        learning_rate: Optional[float] = None,
        weight_decay: Optional[float] = None,
        loss_function: Optional[RegressionLossFunction] = None,
        loss_ceiling: Optional[float] = None,
    ):
        super().__init__(
            uuid=UUID("30c2f4c3-fcb7-4dee-93e6-d6124934ea5e"),
            parameters=dict(
                batch_size=batch_size,
                max_training_epochs=max_training_epochs,
                min_relative_loss_change=min_relative_loss_change,
                patience=patience,
                embedding_dimension=embedding_dimension,
                hidden_layer_dimensions=hidden_layer_dimensions,
                dropout_rate=dropout_rate,
                learning_rate=learning_rate,
                weight_decay=weight_decay,
                loss_function=loss_function,
                loss_ceiling=loss_ceiling,
            ),
        )
