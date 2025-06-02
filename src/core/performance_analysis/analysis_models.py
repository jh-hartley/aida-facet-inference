from dataclasses import dataclass
from typing import Any, Dict, List

from src.core.prompts.confidence_levels import ConfidenceLevel


@dataclass
class PredictionMetrics:
    """Basic metrics for a set of predictions."""

    accuracy: float
    f1_score: float
    precision: float
    recall: float
    total_predictions: int
    correct_predictions: int


@dataclass
class SegmentMetrics:
    """Metrics for a segment of predictions with metadata."""

    segment_key: str
    segment_name: str
    metrics: PredictionMetrics
    sample_size: int


@dataclass
class ConfidenceSegmentMetrics:
    """Metrics for predictions within a confidence segment."""

    confidence_level: ConfidenceLevel
    metrics: PredictionMetrics
    sample_size: int


@dataclass
class CategoryMetrics:
    """Metrics for a product category with friendly name."""

    category_key: str
    category_name: str
    metrics: PredictionMetrics
    sample_size: int


@dataclass
class AttributeMetrics:
    """Metrics for an attribute with friendly name."""

    attribute_key: str
    attribute_name: str
    metrics: PredictionMetrics
    sample_size: int


@dataclass
class GapCountMetrics:
    """Metrics for products with a specific number of gaps."""

    gap_count: int
    metrics: PredictionMetrics
    sample_size: int


@dataclass
class DescriptionLengthMetrics:
    """Metrics for products with different description lengths."""

    length_segment: str  # "short", "medium", "long"
    metrics: PredictionMetrics
    sample_size: int


@dataclass
class CorrelationAnalysis:
    """Analysis of correlation between confidence and accuracy."""

    correlation: float
    sample_size: int


@dataclass
class ExperimentAnalysis:
    """Complete analysis results for an experiment."""

    experiment_key: str
    overall_metrics: PredictionMetrics
    confidence_segments: List[ConfidenceSegmentMetrics]
    category_metrics: List[CategoryMetrics]
    attribute_metrics: List[AttributeMetrics]
    gap_count_metrics: List[GapCountMetrics]
    description_length_metrics: List[DescriptionLengthMetrics]
    confidence_correlation: CorrelationAnalysis
    metadata: Dict[str, Any]
