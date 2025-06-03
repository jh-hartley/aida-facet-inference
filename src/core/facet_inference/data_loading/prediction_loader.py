"""Loader for prediction data from experiments."""

import logging
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.infrastructure.database.input_data.records import (
    HumanRecommendationRecord,
)
from src.core.infrastructure.database.input_data.repositories import (
    RawAttributeRepository,
)
from src.core.infrastructure.database.predictions.records import (
    PredictionResultRecord,
)
from src.core.infrastructure.database.predictions.repositories import (
    PredictionResultRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class PredictionEntry:
    """A single prediction entry for a product attribute."""

    prediction_key: str
    experiment_key: str
    product_key: str
    attribute_key: str
    predicted_value: str
    confidence: float
    recommendation_key: int | None
    correctness_status: bool | None = None
    reasoning: str | None = None
    suggested_value: str | None = None


class PredictionLoader:
    """Loads and structures prediction data from experiments."""

    def __init__(self, session: Session):
        """Initialize the loader.

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.repo = PredictionResultRepository(session)
        self.attribute_repo = RawAttributeRepository(session)

    def load_predictions(
        self, experiment_key: str
    ) -> Sequence[PredictionEntry]:
        """Load all predictions from a specific experiment.

        Args:
            experiment_key: Experiment key to load predictions for

        Returns:
            Sequence of prediction entries
        """
        results = self.repo.get_predictions_by_experiment(experiment_key)

        return [
            PredictionEntry(
                prediction_key=pred.prediction_key,
                experiment_key=experiment_key,
                product_key=pred.product_key,
                attribute_key=pred.attribute_key,
                predicted_value=pred.value,
                confidence=pred.confidence,
                recommendation_key=pred.recommendation_key,
                correctness_status=pred.correctness_status,
                reasoning=pred.reasoning,
                suggested_value=pred.suggested_value,
            )
            for pred in results
        ]

    def validate_predictions(
        self,
        predictions: Sequence[PredictionEntry],
        similarity_threshold: float = 0.95,
    ) -> None:
        """Validate predictions against ground truth.

        Args:
            predictions: Sequence of predictions to validate
            similarity_threshold: Minimum similarity ratio to consider a match
        """
        for entry in predictions:
            if entry.recommendation_key:
                try:
                    logger.info(
                        f"Looking up recommendation with ID "
                        f"{entry.recommendation_key} "
                        f"for prediction {entry.prediction_key} "
                        f"(product: {entry.product_key}, "
                        f"attribute: {entry.attribute_key})"
                    )

                    query = select(HumanRecommendationRecord).where(
                        HumanRecommendationRecord.id
                        == entry.recommendation_key
                    )
                    logger.info(f"Executing query: {query}")

                    ground_truth = self.session.scalars(query).first()

                    if ground_truth:
                        # Compare predicted value with ground truth
                        is_correct = self._fuzzy_match(
                            entry.predicted_value,
                            ground_truth.recommendation,
                            similarity_threshold,
                        )
                        entry.correctness_status = is_correct

                        # Update the database record
                        self.repo.update_prediction_validation(
                            entry.prediction_key,
                            is_correct,
                            ground_truth.recommendation,
                            (
                                entry.reasoning
                                if hasattr(entry, "reasoning")
                                else None
                            ),
                            (
                                entry.suggested_value
                                if hasattr(entry, "suggested_value")
                                else None
                            ),
                        )

                        logger.info(
                            f"Validated prediction for {entry.attribute_key}: "
                            f"predicted='{entry.predicted_value}', "
                            f"ground_truth='{ground_truth.recommendation}', "
                            f"correct={is_correct}, "
                            f"reasoning='{entry.reasoning if hasattr(entry, 'reasoning') else None}', "  # noqa: E501
                            f"suggested_value='{entry.suggested_value if hasattr(entry, 'suggested_value') else None}'"  # noqa: E501
                        )
                    else:
                        logger.warning(
                            f"No recommendation record found with ID "
                            f"{entry.recommendation_key}. "
                            f"Query returned no results.\n"
                            f"SQL query was: {query}"
                        )

                        count_query = select(HumanRecommendationRecord)
                        total_records = self.session.scalars(count_query).all()
                        logger.info(
                            f"Total records in human_recommendations table: "
                            f"{len(total_records)}"
                        )

                except Exception as e:
                    logger.error(
                        f"Error validating prediction for recommendation "
                        f"{entry.recommendation_key}: {str(e)}"
                    )

    def get_predictions_by_product(
        self, experiment_key: str, product_key: str
    ) -> Sequence[PredictionEntry]:
        """Get predictions for a specific product in an experiment.

        Args:
            experiment_key: Experiment key
            product_key: Product key to filter by

        Returns:
            Sequence of prediction entries for the product
        """
        return [
            entry
            for entry in self.load_predictions(experiment_key)
            if entry.product_key == product_key
        ]

    def get_predictions_by_attribute(
        self, experiment_key: str, attribute_key: str
    ) -> Sequence[PredictionEntry]:
        """Get predictions for a specific attribute in an experiment.

        Args:
            experiment_key: Experiment key
            attribute_key: Attribute key to filter by

        Returns:
            Sequence of prediction entries for the attribute
        """
        return [
            entry
            for entry in self.load_predictions(experiment_key)
            if entry.attribute_key == attribute_key
        ]

    def get_unique_product_keys(self, experiment_key: str) -> set[str]:
        """Get all unique product keys in the predictions.

        Args:
            experiment_key: Experiment key

        Returns:
            Set of product keys
        """
        return {
            entry.product_key
            for entry in self.load_predictions(experiment_key)
        }

    def get_unique_attribute_keys(self, experiment_key: str) -> set[str]:
        """Get all unique attribute keys in the predictions.

        Args:
            experiment_key: Experiment key

        Returns:
            Set of attribute keys
        """
        return {
            entry.attribute_key
            for entry in self.load_predictions(experiment_key)
        }

    def calculate_accuracy(
        self, predictions: Sequence[PredictionEntry]
    ) -> tuple[int, float]:
        """Calculate accuracy of validated predictions.

        Args:
            predictions: Sequence of predictions

        Returns:
            Tuple of (validated_count, accuracy)
        """
        validated = [
            p for p in predictions if p.correctness_status is not None
        ]
        if not validated:
            return 0, 0.0

        correct = sum(1 for p in validated if p.correctness_status)
        return len(validated), correct / len(validated)

    def get_predictions_by_experiment(
        self, experiment_key: str
    ) -> list[PredictionEntry]:
        """Get all predictions for an experiment.

        Args:
            experiment_key: Experiment key

        Returns:
            List of prediction entries
        """
        predictions = self.session.scalars(
            select(PredictionResultRecord).where(
                PredictionResultRecord.experiment_key == experiment_key
            )
        ).all()

        return [
            PredictionEntry(
                prediction_key=pred.prediction_key,
                experiment_key=experiment_key,
                product_key=pred.product_key,
                attribute_key=pred.attribute_key,
                predicted_value=pred.value,
                confidence=pred.confidence,
                recommendation_key=pred.recommendation_key,
                correctness_status=pred.correctness_status,
                reasoning=pred.reasoning,
                suggested_value=pred.suggested_value,
            )
            for pred in predictions
        ]

    def _fuzzy_match(
        self, predicted: str, ground_truth: str, threshold: float
    ) -> bool:
        """Check if predicted value matches ground truth using fuzzy matching.

        Args:
            predicted: Predicted value
            ground_truth: Ground truth value
            threshold: Minimum similarity ratio to consider a match

        Returns:
            True if values match, False otherwise
        """
        # Normalize strings
        predicted = predicted.lower().strip()
        ground_truth = ground_truth.lower().strip()

        # Check for exact match first
        if predicted == ground_truth:
            return True

        # Calculate similarity ratio
        from difflib import SequenceMatcher

        similarity = SequenceMatcher(None, predicted, ground_truth).ratio()

        return similarity >= threshold
