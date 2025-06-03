"""Prediction data loading and evaluation for facet predictions."""

from dataclasses import dataclass
from typing import Sequence

from sqlalchemy.orm import Session

from src.core.infrastructure.database.predictions.repositories import PredictionResultRepository


@dataclass
class PredictionEntry:
    """A single prediction entry for a product attribute."""
    product_key: str
    attribute_key: str
    predicted_value: str
    confidence: float
    recommendation_key: int | None
    correctness_status: bool | None = None


class PredictionLoader:
    """Loads and structures prediction data from experiment results."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = PredictionResultRepository(session)

    def load_predictions(
        self, experiment_key: str
    ) -> Sequence[PredictionEntry]:
        """
        Load all predictions from a specific experiment.
        
        Args:
            experiment_key: The key of the experiment to load predictions from
            
        Returns:
            A sequence of PredictionEntry objects containing prediction information
        """
        predictions = self.repository.get_predictions_by_experiment(experiment_key)
        
        return [
            PredictionEntry(
                product_key=pred.product_key,
                attribute_key=pred.attribute_key,
                predicted_value=pred.value,
                confidence=pred.confidence,
                recommendation_key=pred.recommendation_key,
            )
            for pred in predictions
        ]

    def get_predictions_by_product(
        self, experiment_key: str, product_key: str
    ) -> Sequence[PredictionEntry]:
        """Get predictions for a specific product in an experiment."""
        return [
            entry
            for entry in self.load_predictions(experiment_key)
            if entry.product_key == product_key
        ]

    def get_predictions_by_attribute(
        self, experiment_key: str, attribute_key: str
    ) -> Sequence[PredictionEntry]:
        """Get predictions for a specific attribute in an experiment."""
        return [
            entry
            for entry in self.load_predictions(experiment_key)
            if entry.attribute_key == attribute_key
        ]

    def get_unique_products(self, experiment_key: str) -> set[str]:
        """Get set of unique product keys in predictions."""
        return {
            entry.product_key
            for entry in self.load_predictions(experiment_key)
        }

    def get_unique_attributes(self, experiment_key: str) -> set[str]:
        """Get set of unique attribute keys in predictions."""
        return {
            entry.attribute_key
            for entry in self.load_predictions(experiment_key)
        } 