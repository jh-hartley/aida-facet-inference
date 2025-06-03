import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from src.common.clock import clock
from src.common.db import uuid
from src.core.infrastructure.database.predictions.repositories import PredictionExperimentRepository
from src.core.infrastructure.database.predictions.records import (
    PredictionExperimentRecord,
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
        self.session = session
        self.description = description
        self.metadata = metadata or {}
        self.repository = PredictionExperimentRepository(session)

    def create_experiment(self) -> str:
        """Create a new experiment record and return its key."""
        experiment_key = str(uuid())
        experiment = PredictionExperimentRecord(
            experiment_key=experiment_key,
            experiment_metadata={
                "description": self.description or "No description provided",
                "timestamp": clock.now().isoformat(),
                **(self.metadata or {}),
            },
            started_at=clock.now(),
        )
        self.repository.create(experiment)
        self.session.commit()
        logger.info(f"Created experiment {experiment_key}")
        return experiment_key

    def update_metrics(
        self,
        experiment_key: str,
        total_predictions: int,
        total_products: int,
        elapsed_time: float,
    ) -> None:
        """Update experiment metrics after completion."""
        experiment = self.repository.get_by_experiment_key(experiment_key)
        experiment.completed_at = datetime.now(timezone.utc)
        experiment.total_predictions = total_predictions
        experiment.total_products = total_products
        experiment.average_time_per_prediction = (
            elapsed_time / total_predictions if total_predictions > 0 else None
        )
        self.session.add(experiment)
        self.session.commit()
        logger.info(
            f"Updated metrics for experiment {experiment_key}: "
            f"{total_predictions} predictions, {total_products} products, "
            f"{elapsed_time:.2f}s elapsed"
        ) 