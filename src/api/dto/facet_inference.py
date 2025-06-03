from pydantic import BaseModel

from src.core.domain.models import FacetPrediction


class FacetPredictionResponse(BaseModel):
    """Response model for a single facet prediction."""

    prediction: FacetPrediction


class FacetPredictionsResponse(BaseModel):
    """Response model for multiple facet predictions."""

    predictions: list[FacetPrediction]
