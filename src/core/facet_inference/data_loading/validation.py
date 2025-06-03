"""Validation utilities for predictions."""

from difflib import SequenceMatcher


def fuzzy_match(
    predicted: str, ground_truth: str, threshold: float = 0.95
) -> bool:
    """Check if two strings match using fuzzy matching.

    Args:
        predicted: The predicted value
        ground_truth: The ground truth value
        threshold: Similarity threshold (0.0 to 1.0)

    Returns:
        True if the strings match within the threshold
    """
    # Normalize strings
    predicted = predicted.lower().strip()
    ground_truth = ground_truth.lower().strip()

    # Exact match
    if predicted == ground_truth:
        return True

    # Calculate similarity ratio
    similarity = SequenceMatcher(None, predicted, ground_truth).ratio()
    return similarity >= threshold
