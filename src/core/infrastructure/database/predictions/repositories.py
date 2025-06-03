"""Repositories for prediction results."""

from datetime import datetime, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from .records import ExperimentRecord, PredictionResultRecord


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
        self.session.add(experiment)
        self.session.commit()
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
    ) -> None:
        """Update experiment metrics.
        
        Args:
            experiment_key: Experiment key
            total_predictions: Total number of predictions
            validated_predictions: Number of validated predictions
            correct_predictions: Number of correct predictions
            accuracy: Overall accuracy
        """
        experiment = self.get_experiment(experiment_key)
        if experiment:
            experiment.total_predictions = total_predictions
            experiment.total_products = validated_predictions  # Using validated_predictions as total_products
            experiment.average_time_per_prediction = accuracy  # Using accuracy as average_time_per_prediction
            self.session.commit()

    def complete_experiment(self, experiment_key: str) -> None:
        """Mark an experiment as completed.
        
        Args:
            experiment_key: Experiment key
        """
        experiment = self.get_experiment(experiment_key)
        if experiment:
            experiment.completed_at = datetime.now(timezone.utc)
            self.session.commit()


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
        """Create a new prediction result.
        
        Args:
            experiment_key: Experiment key
            product_key: Product key
            attribute_key: Attribute key
            value: Predicted value
            confidence: Prediction confidence
            recommendation_key: Optional recommendation key (ID from human_recommendations table)
            actual_value: The actual ground truth value
            correctness_status: Whether the prediction is correct
            reasoning: Explanation for why this value was chosen
            suggested_value: Suggested value when the correct value is not in the allowed list
            
        Returns:
            Created prediction result record
        """
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
        self.session.add(prediction)
        self.session.commit()
        return prediction

    def update_prediction_validation(
        self, 
        prediction_key: str, 
        is_correct: bool, 
        actual_value: str,
        reasoning: str | None = None,
        suggested_value: str | None = None,
    ) -> None:
        """Update prediction validation status and actual value.
        
        Args:
            prediction_key: Prediction key
            is_correct: Whether the prediction is correct
            actual_value: The actual ground truth value
            reasoning: Explanation for why this value was chosen
            suggested_value: Suggested value when the correct value is not in the allowed list
        """
        prediction = self.session.get(PredictionResultRecord, prediction_key)
        if prediction:
            prediction.correctness_status = is_correct
            prediction.actual_value = actual_value
            if reasoning is not None:
                prediction.reasoning = reasoning
            if suggested_value is not None:
                prediction.suggested_value = suggested_value
            self.session.commit()

    def get_predictions_by_experiment(
        self, experiment_key: str
    ) -> list[PredictionResultRecord]:
        """Get all predictions for an experiment.
        
        Args:
            experiment_key: Experiment key
            
        Returns:
            List of prediction result records
        """
        return list(
            self.session.scalars(
                select(PredictionResultRecord).where(
                    PredictionResultRecord.experiment_key == experiment_key
                )
            )
        )

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
        return list(
            self.session.scalars(
                select(PredictionResultRecord).where(
                    PredictionResultRecord.experiment_key == experiment_key,
                    PredictionResultRecord.product_key == product_key,
                )
            )
        )