"""Facet inference system for product attribute prediction.

This module provides a service for predicting product facet labels using LLMs.
The main entry point is the FacetInferenceService class, which provides methods
for single and concurrent facet predictions.
"""

from src.core.facet_inference.models import (
    FacetDefinition,
    FacetPrediction,
    ProductInfo,
)
from src.core.facet_inference.service import FacetInferenceService

__all__ = [
    "FacetInferenceService",
    "FacetDefinition",
    "FacetPrediction",
    "ProductInfo",
]
