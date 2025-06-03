import logging
from typing import Any
from src.common.clock import clock


from sqlalchemy.orm import Session

from src.core.infrastructure.database.predictions.repositories import (
    ExperimentRepository,
)

logger = logging.getLogger(__name__)


class ExperimentManager:
    """Manages the lifecycle of prediction experiments."""

    def __init__(
        self,
        session: Session,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Initialize the manager.
        
        Args:
            session: SQLAlchemy session
            description: Optional experiment description
            metadata: Optional experiment metadata
        """
        self.session = session
        self.description = description
        self.metadata = metadata or {}
        self.repository = ExperimentRepository(session)

    def create_experiment(self) -> str:
        """Create a new experiment record and return its key.
        
        Returns:
            Experiment key
        """
        experiment = self.repository.create_experiment(
            name=f"Experiment {clock.now().isoformat()}",
            description=self.description,
        )
        logger.info(f"Created experiment {experiment.experiment_key}")
        return experiment.experiment_key

    def update_metrics(
        self,
        experiment_key: str,
        total_predictions: int,
        validated_predictions: int,
        correct_predictions: int,
        accuracy: float,
    ) -> None:
        """Update experiment metrics after completion.
        
        Args:
            experiment_key: Experiment key
            total_predictions: Total number of predictions
            validated_predictions: Number of validated predictions
            correct_predictions: Number of correct predictions
            accuracy: Overall accuracy
        """
        self.repository.update_experiment_metrics(
            experiment_key=experiment_key,
            total_predictions=total_predictions,
            validated_predictions=validated_predictions,
            correct_predictions=correct_predictions,
            accuracy=accuracy,
        )
        logger.info(
            f"Updated metrics for experiment {experiment_key}: "
            f"{total_predictions} total predictions, "
            f"{validated_predictions} validated, "
            f"{correct_predictions} correct, "
            f"{accuracy:.2%} accuracy"
        )

    def complete_experiment(self, experiment_key: str) -> None:
        """Mark an experiment as completed.
        
        Args:
            experiment_key: Experiment key
        """
        self.repository.complete_experiment(experiment_key)
        logger.info(f"Marked experiment {experiment_key} as completed") 