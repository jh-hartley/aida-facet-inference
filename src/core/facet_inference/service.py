from asyncio import gather
from typing import Sequence

from src.core.facet_inference.inference import ProductFacetPredictor
from src.core.facet_inference.models import (
    FacetDefinition,
    FacetPrediction,
    ProductInfo,
)


class FacetInferenceService:
    """Service layer for facet inference operations."""

    def __init__(self, predictor: ProductFacetPredictor | None = None):
        self._predictor = predictor or ProductFacetPredictor()

    async def predict_facet(
        self,
        product: ProductInfo,
        facet: FacetDefinition,
    ) -> FacetPrediction:
        """
        Predict labels for a single product facet.
        """
        return await self._predictor.predict(product=product, facet=facet)

    async def predict_multiple_facets(
        self,
        product: ProductInfo,
        facets: Sequence[FacetDefinition],
    ) -> list[FacetPrediction]:
        """
        Predict labels for multiple product facets concurrently.
        """
        predictions = await gather(
            *(self.predict_facet(product, facet) for facet in facets)
        )
        return list(predictions)
