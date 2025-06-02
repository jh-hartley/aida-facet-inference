from asyncio import gather
from typing import Sequence

from src.core.facet_inference.inference import ProductFacetPredictor
from src.core.facet_inference.models import FacetPrediction
from src.core.models import ProductDetails, ProductGaps
from src.core.types import ProductAttributeGap


class FacetInferenceService:
    """Service layer for facet inference operations."""

    def __init__(
        self,
        product_details: ProductDetails,
        product_gaps: ProductGaps,
        predictor: ProductFacetPredictor | None = None,
    ):
        self._predictor = predictor or ProductFacetPredictor(
            product_details=product_details,
            product_gaps=product_gaps,
        )

    async def predict_attribute(
        self,
        gap: ProductAttributeGap,
    ) -> FacetPrediction:
        """
        Predict a value for a missing attribute.

        Args:
            gap: Information about the missing attribute and its allowed values

        Returns:
            Prediction result with value and confidence
        """
        return await self._predictor.apredict_single_gap(gap)

    async def predict_multiple_attributes(
        self,
        gaps: Sequence[ProductAttributeGap],
    ) -> list[FacetPrediction]:
        """
        Predict values for multiple missing attributes concurrently.

        Args:
            gaps: List of missing attributes and their allowed values

        Returns:
            List of prediction results with values and confidence
        """
        predictions = await gather(
            *(self.predict_attribute(gap) for gap in gaps)
        )
        return list(predictions)
