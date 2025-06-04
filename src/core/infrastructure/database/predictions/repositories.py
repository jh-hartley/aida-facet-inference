"""Repositories for prediction results."""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .records import ExperimentRecord, PredictionResultRecord

logger = logging.getLogger(__name__)


class ExperimentRepository:
    """Repository for experiment records."""

    def __init__(self, session: Session):
        """Initialize the repository.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def create_experiment(
        self, name: str, description: str | None = None
    ) -> ExperimentRecord:
        """Create a new experiment.

        Args:
            name: Experiment name
            description: Optional experiment description

        Returns:
            Created experiment record
        """
        experiment = ExperimentRecord(
            experiment_key=str(uuid.uuid4()),
            experiment_metadata={
                "name": name,
                "description": description,
            },
            started_at=datetime.now(timezone.utc),
        )
        logger.debug(f"Creating experiment with key: {experiment.experiment_key}")
        self.session.add(experiment)
        self.session.commit()
        logger.debug(f"Committed experiment {experiment.experiment_key}")
        return experiment

    def get_experiment(self, experiment_key: str) -> ExperimentRecord | None:
        """Get an experiment by key.

        Args:
            experiment_key: Experiment key

        Returns:
            Experiment record if found, None otherwise
        """
        return self.session.get(ExperimentRecord, experiment_key)

    def update_experiment_metrics(
        self,
        experiment_key: str,
        total_predictions: int,
        validated_predictions: int,
        correct_predictions: int,
        accuracy: float,
        average_time_per_prediction: float,
    ) -> None:
        """Update experiment metrics.

        Args:
            experiment_key: Experiment key
            total_predictions: Total number of predictions
            validated_predictions: Number of validated predictions
            correct_predictions: Number of correct predictions
            accuracy: Overall accuracy
            average_time_per_prediction: Average time per prediction
        """
        experiment = self.get_experiment(experiment_key)
        if experiment:
            logger.debug(f"Updating metrics for experiment {experiment_key}")
            experiment.total_predictions = total_predictions
            experiment.total_products = validated_predictions
            experiment.average_time_per_prediction = (
                average_time_per_prediction
            )
            experiment.correct_predictions = correct_predictions
            experiment.accuracy = accuracy
            self.session.commit()
            logger.debug(f"Committed metrics update for experiment {experiment_key}")

    def complete_experiment(self, experiment_key: str) -> None:
        """Mark an experiment as completed.

        Args:
            experiment_key: Experiment key
        """
        experiment = self.get_experiment(experiment_key)
        if experiment:
            logger.debug(f"Completing experiment {experiment_key}")
            experiment.completed_at = datetime.now(timezone.utc)
            self.session.commit()
            logger.debug(f"Committed completion for experiment {experiment_key}")


class PredictionResultRepository:
    """Repository for prediction result records."""

    def __init__(self, session: Session):
        """Initialize the repository.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def create_prediction(
        self,
        experiment_key: str,
        product_key: str,
        attribute_key: str,
        value: str,
        confidence: float,
        recommendation_key: int | None = None,
        actual_value: str | None = None,
        correctness_status: bool | None = None,
        reasoning: str | None = None,
        suggested_value: str | None = None,
    ) -> PredictionResultRecord:
        prediction = PredictionResultRecord(
            prediction_key=str(uuid.uuid4()),
            experiment_key=experiment_key,
            product_key=product_key,
            attribute_key=attribute_key,
            value=value,
            confidence=confidence,
            recommendation_key=recommendation_key,
            actual_value=actual_value,
            correctness_status=correctness_status,
            reasoning=reasoning,
            suggested_value=suggested_value,
        )
        logger.debug(
            f"Creating prediction with key: {prediction.prediction_key} "
            f"for experiment: {experiment_key}, "
            f"product: {product_key}, "
            f"attribute: {attribute_key}, "
            f"value: {value}"
        )
        self.session.add(prediction)
        logger.debug(f"Added prediction {prediction.prediction_key} to session")
        self.session.commit()
        logger.debug(f"Committed prediction {prediction.prediction_key}")
        
        # Verify the prediction was actually stored
        stored_prediction = self.session.get(PredictionResultRecord, prediction.prediction_key)
        if stored_prediction:
            logger.debug(f"Verified prediction {prediction.prediction_key} exists in database")
        else:
            logger.error(f"Failed to verify prediction {prediction.prediction_key} in database!")
            
        return prediction

    def update_prediction_validation(
        self,
        prediction_key: str,
        is_correct: bool,
        actual_value: str,
        reasoning: str | None = None,
        suggested_value: str | None = None,
    ) -> None:
        prediction = self.session.get(PredictionResultRecord, prediction_key)
        if prediction:
            logger.debug(f"Updating validation for prediction {prediction_key}")
            prediction.correctness_status = is_correct
            prediction.actual_value = actual_value
            if reasoning is not None:
                prediction.reasoning = reasoning
            if suggested_value is not None:
                prediction.suggested_value = suggested_value
            self.session.commit()
            logger.debug(f"Committed validation update for prediction {prediction_key}")

    def get_predictions_by_experiment(
        self, experiment_key: str
    ) -> list[PredictionResultRecord]:
        """Get all predictions for an experiment.

        Args:
            experiment_key: Experiment key

        Returns:
            List of prediction result records
        """
        logger.debug(f"Getting predictions for experiment {experiment_key}")
        predictions = list(
            self.session.scalars(
                select(PredictionResultRecord).where(
                    PredictionResultRecord.experiment_key == experiment_key
                )
            )
        )
        logger.debug(f"Found {len(predictions)} predictions for experiment {experiment_key}")
        return predictions

    def get_predictions_by_product(
        self, experiment_key: str, product_key: str
    ) -> list[PredictionResultRecord]:
        """Get all predictions for a product in an experiment.

        Args:
            experiment_key: Experiment key
            product_key: Product key

        Returns:
            List of prediction result records
        """
        logger.debug(
            f"Getting predictions for experiment {experiment_key} "
            f"and product {product_key}"
        )
        predictions = list(
            self.session.scalars(
                select(PredictionResultRecord).where(
                    PredictionResultRecord.experiment_key == experiment_key,
                    PredictionResultRecord.product_key == product_key,
                )
            )
        )
        logger.debug(
            f"Found {len(predictions)} predictions for experiment {experiment_key} "
            f"and product {product_key}"
        )
        return predictions
