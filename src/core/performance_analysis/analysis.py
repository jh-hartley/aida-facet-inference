from typing import Sequence

from src.core.infrastructure.database.predictions.repositories import ExperimentRepository, PredictionResultRepository
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.domain.confidence_levels import ConfidenceLevel
from src.core.domain.repositories import (
    FacetIdentificationRepository,
)
from src.core.infrastructure.database.input_data.records import (
    RawRecommendationRecord,
)
from src.core.infrastructure.database.predictions.records import (
    PredictionResultRecord,
)
from src.core.performance_analysis.analysis_models import (
    AttributeMetrics,
    CategoryMetrics,
    ConfidenceSegmentMetrics,
    CorrelationAnalysis,
    DescriptionLengthMetrics,
    ExperimentAnalysis,
    GapCountMetrics,
    PredictionMetrics,
)


class PredictionAnalyzer:
    """Analyzer for prediction results."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = FacetIdentificationRepository(session)
        self.experiment_repo = ExperimentRepository(session)
        self.result_repo = PredictionResultRepository(session)

    def get_experiment_results(
        self, experiment_key: str
    ) -> list[PredictionResultRecord]:
        """Get all results for an experiment."""
        return self.result_repo.get_predictions_by_experiment(experiment_key)

    def get_ground_truth(
        self, product_key: str, attribute_key: str
    ) -> str | None:
        """Get ground truth value for a product-attribute pair."""
        result = self.session.scalar(
            select(RawRecommendationRecord).where(
                RawRecommendationRecord.product_key == product_key,
                RawRecommendationRecord.attribute_key == attribute_key,
            )
        )
        return result.value if result else None

    def calculate_basic_metrics(
        self, results: Sequence[PredictionResultRecord]
    ) -> PredictionMetrics:
        """Calculate basic accuracy metrics for predictions."""
        total = len(results)
        if total == 0:
            return PredictionMetrics(0.0, 0.0, 0.0, 0.0, 0, 0)

        correct = 0
        true_positives = 0
        false_positives = 0
        false_negatives = 0

        for result in results:
            ground_truth = self.get_ground_truth(
                result.product_key, result.attribute_key
            )
            if ground_truth is None:
                continue

            if result.value == ground_truth:
                correct += 1
                true_positives += 1
            else:
                false_positives += 1
                false_negatives += 1

        accuracy = correct / total if total > 0 else 0.0
        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0.0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0.0
        )
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return PredictionMetrics(
            accuracy=accuracy,
            f1_score=f1,
            precision=precision,
            recall=recall,
            total_predictions=total,
            correct_predictions=correct,
        )

    def analyze_by_confidence(
        self, results: Sequence[PredictionResultRecord]
    ) -> list[ConfidenceSegmentMetrics]:
        """Analyze prediction performance by confidence segments."""
        segments: dict[ConfidenceLevel, list[PredictionResultRecord]] = {
            level: [] for level in ConfidenceLevel
        }

        # Group predictions by confidence level
        for result in results:
            level = ConfidenceLevel.from_score(result.confidence)
            segments[level].append(result)

        # Calculate metrics for each segment
        return [
            ConfidenceSegmentMetrics(
                confidence_level=level,
                metrics=self.calculate_basic_metrics(predictions),
                sample_size=len(predictions),
            )
            for level, predictions in segments.items()
            if predictions  # Only include segments with predictions
        ]

    def analyze_by_category(
        self, results: Sequence[PredictionResultRecord]
    ) -> list[CategoryMetrics]:
        """Analyze prediction performance by product category."""
        category_metrics: dict[
            str, tuple[str, list[PredictionResultRecord]]
        ] = {}

        # Get all unique categories from the results
        for result in results:
            product_categories = (
                self.repository.product_category_repo.get_by_product_key(
                    result.product_key
                )
            )

            for category in product_categories:
                if category.category_key not in category_metrics:
                    category_metrics[category.category_key] = (
                        category.friendly_name,
                        [],
                    )
                category_metrics[category.category_key][1].append(result)

        # Calculate metrics for each category
        return [
            CategoryMetrics(
                category_key=category_key,
                category_name=friendly_name,
                metrics=self.calculate_basic_metrics(predictions),
                sample_size=len(predictions),
            )
            for category_key, (
                friendly_name,
                predictions,
            ) in category_metrics.items()
        ]

    def analyze_by_attribute(
        self, results: Sequence[PredictionResultRecord]
    ) -> list[AttributeMetrics]:
        """Analyze prediction performance by attribute."""
        attribute_metrics: dict[
            str, tuple[str, list[PredictionResultRecord]]
        ] = {}

        # Group results by attribute
        for result in results:
            if result.attribute_key not in attribute_metrics:
                attribute = self.repository.attribute_repo.get_by_id(
                    result.attribute_key
                )
                attribute_metrics[result.attribute_key] = (
                    attribute.friendly_name,
                    [],
                )
            attribute_metrics[result.attribute_key][1].append(result)

        # Calculate metrics for each attribute
        return [
            AttributeMetrics(
                attribute_key=attribute_key,
                attribute_name=friendly_name,
                metrics=self.calculate_basic_metrics(predictions),
                sample_size=len(predictions),
            )
            for attribute_key, (
                friendly_name,
                predictions,
            ) in attribute_metrics.items()
        ]

    def analyze_by_gap_count(
        self, results: Sequence[PredictionResultRecord]
    ) -> list[GapCountMetrics]:
        """Analyze prediction performance by number of gaps in product."""
        gap_count_metrics: dict[int, list[PredictionResultRecord]] = {}

        # Get gap counts for each product
        product_gap_counts: dict[str, int] = {}
        for result in results:
            if result.product_key not in product_gap_counts:
                # flake8: noqa: E501
                gaps = self.repository.product_attribute_gap_repo.get_by_product_key(
                    result.product_key
                )
                product_gap_counts[result.product_key] = len(gaps)

        # Group results by gap count
        for result in results:
            gap_count = product_gap_counts[result.product_key]
            if gap_count not in gap_count_metrics:
                gap_count_metrics[gap_count] = []
            gap_count_metrics[gap_count].append(result)

        # Calculate metrics for each gap count
        return [
            GapCountMetrics(
                gap_count=gap_count,
                metrics=self.calculate_basic_metrics(predictions),
                sample_size=len(predictions),
            )
            for gap_count, predictions in gap_count_metrics.items()
        ]

    def analyze_by_description_length(
        self, results: Sequence[PredictionResultRecord]
    ) -> list[DescriptionLengthMetrics]:
        """Analyze prediction performance by description length segments."""
        length_metrics: dict[str, list[PredictionResultRecord]] = {
            "short": [],
            "medium": [],
            "long": [],
        }

        # Get description lengths for each product
        product_lengths: dict[str, int] = {}
        for result in results:
            if result.product_key not in product_lengths:
                rich_text = self.repository.rich_text_repo.find_by_product_key(
                    result.product_key
                )
                total_length = sum(len(rt.content) for rt in rich_text)
                product_lengths[result.product_key] = total_length

        # Group results by length segment
        for result in results:
            length = product_lengths[result.product_key]
            if length < 500:
                segment = "short"
            elif length < 2000:
                segment = "medium"
            else:
                segment = "long"
            length_metrics[segment].append(result)

        # Calculate metrics for each length segment
        return [
            DescriptionLengthMetrics(
                length_segment=segment,
                metrics=self.calculate_basic_metrics(predictions),
                sample_size=len(predictions),
            )
            for segment, predictions in length_metrics.items()
            if predictions  # Only include segments with predictions
        ]

    def get_correlation_analysis(
        self, results: Sequence[PredictionResultRecord]
    ) -> CorrelationAnalysis:
        """Calculate correlation between confidence and accuracy."""
        confidences = []
        accuracies = []

        for result in results:
            ground_truth = self.get_ground_truth(
                result.product_key, result.attribute_key
            )
            if ground_truth is not None:
                confidences.append(result.confidence)
                accuracies.append(1.0 if result.value == ground_truth else 0.0)

        if not confidences:
            return CorrelationAnalysis(correlation=0.0, sample_size=0)

        correlation = np.corrcoef(confidences, accuracies)[0, 1]
        return CorrelationAnalysis(
            correlation=correlation,
            sample_size=len(confidences),
        )

    def analyze_experiment(self, experiment_key: str) -> ExperimentAnalysis:
        """Perform comprehensive analysis of an experiment."""
        results = self.get_experiment_results(experiment_key)
        experiment = self.experiment_repo.get_experiment(experiment_key)

        return ExperimentAnalysis(
            experiment_key=experiment_key,
            overall_metrics=self.calculate_basic_metrics(results),
            confidence_segments=self.analyze_by_confidence(results),
            category_metrics=self.analyze_by_category(results),
            attribute_metrics=self.analyze_by_attribute(results),
            gap_count_metrics=self.analyze_by_gap_count(results),
            description_length_metrics=self.analyze_by_description_length(
                results
            ),
            confidence_correlation=self.get_correlation_analysis(results),
            metadata=experiment.metadata if experiment else {},
        )
