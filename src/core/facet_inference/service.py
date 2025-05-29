from asyncio import gather
from typing import Sequence

from src.core.facet_inference.inference import ProductFacetPredictor
from src.core.facet_inference.models import FacetPrediction
from src.core.models import ProductDetails, ProductGaps


class FacetInferenceService:
    """Service layer for facet inference operations."""

    def __init__(self, predictor: ProductFacetPredictor | None = None):
        self._predictor = predictor or ProductFacetPredictor()

    async def predict_attribute(
        self,
        product: ProductDetails,
        gap: ProductGaps,
    ) -> FacetPrediction:
        """
        Predict a value for a missing attribute.

        Args:
            product: Complete product information
            gap: Information about the missing attribute and its allowed values

        Returns:
            Prediction result with value and confidence
        """
        return await self._predictor.predict(product=product, gap=gap)

    async def predict_multiple_attributes(
        self,
        product: ProductDetails,
        gaps: Sequence[ProductGaps],
    ) -> list[FacetPrediction]:
        """
        Predict values for multiple missing attributes concurrently.

        Args:
            product: Complete product information
            gaps: List of missing attributes and their allowed values

        Returns:
            List of prediction results with values and confidence
        """
        predictions = await gather(
            *(self.predict_attribute(product, gap) for gap in gaps)
        )
        return list(predictions)
