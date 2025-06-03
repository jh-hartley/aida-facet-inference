"""Evaluation of facet predictions against ground truth."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from .ground_truth_loader import GroundTruthLoader
from .prediction_loader import PredictionLoader


@dataclass
class EvaluationResult:
    """Results of evaluating predictions against ground truth."""

    total_predictions: int
    correct_predictions: int
    accuracy: float
    confidence_threshold: float | None = None
    attribute_breakdown: dict[str, float] | None = None
    product_breakdown: dict[str, float] | None = None


class Evaluator:
    """Evaluates predictions against ground truth data."""

    def __init__(self, session: Session):
        self.session = session
        self.ground_truth_loader = GroundTruthLoader(session)
        self.prediction_loader = PredictionLoader(session)

    def evaluate_experiment(
        self,
        experiment_key: str,
        confidence_threshold: float | None = None,
        include_breakdowns: bool = False,
    ) -> EvaluationResult:
        ground_truth = {
            (entry.product_key, entry.attribute_key): entry
            for entry in self.ground_truth_loader.load_ground_truth()
        }

        predictions = self.prediction_loader.load_predictions(
            experiment_key
        )  # noqa: E501

        if confidence_threshold is not None:
            predictions = [
                pred
                for pred in predictions
                if pred.confidence >= confidence_threshold
            ]

        correct = 0
        attribute_correct = {}
        product_correct = {}

        for pred in predictions:
            key = (pred.product_key, pred.attribute_key)
            if key not in ground_truth:
                continue

            truth = ground_truth[key]
            is_correct = pred.predicted_value == truth.ground_truth_value

            if is_correct:
                correct += 1

                # Update attribute breakdown
                if include_breakdowns:
                    if pred.attribute_key not in attribute_correct:
                        attribute_correct[pred.attribute_key] = 0
                    attribute_correct[pred.attribute_key] += 1

                    # Update product breakdown
                    if pred.product_key not in product_correct:
                        product_correct[pred.product_key] = 0
                    product_correct[pred.product_key] += 1

        # Calculate accuracy
        total = len(predictions)
        accuracy = correct / total if total > 0 else 0.0

        # Calculate breakdowns if requested
        attribute_breakdown = None
        if include_breakdowns:
            attribute_breakdown = {
                attr: count / total
                for attr, count in attribute_correct.items()
            }

        product_breakdown = None
        if include_breakdowns:
            product_breakdown = {
                prod: count / total for prod, count in product_correct.items()
            }

        return EvaluationResult(
            total_predictions=total,
            correct_predictions=correct,
            accuracy=accuracy,
            confidence_threshold=confidence_threshold,
            attribute_breakdown=attribute_breakdown,
            product_breakdown=product_breakdown,
        )

    def evaluate_by_attribute(
        self,
        experiment_key: str,
        attribute_key: str,
        confidence_threshold: float | None = None,
    ) -> EvaluationResult:
        """Evaluate predictions for a specific attribute."""
        ground_truth = {
            (entry.product_key, entry.attribute_key): entry
            for entry in self.ground_truth_loader.get_ground_truth_by_attribute(  # noqa: E501
                attribute_key
            )
        }

        predictions = self.prediction_loader.get_predictions_by_attribute(
            experiment_key, attribute_key
        )

        if confidence_threshold is not None:
            predictions = [
                pred
                for pred in predictions
                if pred.confidence >= confidence_threshold
            ]

        # Count correct predictions
        correct = sum(
            1
            for pred in predictions
            if (pred.product_key, pred.attribute_key) in ground_truth
            and pred.predicted_value
            == ground_truth[
                (pred.product_key, pred.attribute_key)
            ].ground_truth_value
        )

        total = len(predictions)
        accuracy = correct / total if total > 0 else 0.0

        return EvaluationResult(
            total_predictions=total,
            correct_predictions=correct,
            accuracy=accuracy,
            confidence_threshold=confidence_threshold,
        )

    def evaluate_by_product(
        self,
        experiment_key: str,
        product_key: str,
        confidence_threshold: float | None = None,
    ) -> EvaluationResult:
        """Evaluate predictions for a specific product."""
        # Load ground truth and predictions for this product
        ground_truth = {
            (entry.product_key, entry.attribute_key): entry
            for entry in self.ground_truth_loader.get_ground_truth_by_product(
                product_key
            )
        }

        predictions = self.prediction_loader.get_predictions_by_product(
            experiment_key, product_key
        )

        # Filter by confidence if threshold provided
        if confidence_threshold is not None:
            predictions = [
                pred
                for pred in predictions
                if pred.confidence >= confidence_threshold
            ]

        # Count correct predictions
        correct = sum(
            1
            for pred in predictions
            if (pred.product_key, pred.attribute_key) in ground_truth
            and pred.predicted_value
            == ground_truth[
                (pred.product_key, pred.attribute_key)
            ].ground_truth_value
        )

        total = len(predictions)
        accuracy = correct / total if total > 0 else 0.0

        return EvaluationResult(
            total_predictions=total,
            correct_predictions=correct,
            accuracy=accuracy,
            confidence_threshold=confidence_threshold,
        )
