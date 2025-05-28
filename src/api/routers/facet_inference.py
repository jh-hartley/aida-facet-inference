from typing import Sequence

from fastapi import APIRouter, Depends

from src.api.dto.facet_inference import (
    FacetDefinitionRequest,
    FacetPredictionResponse,
    FacetPredictionsResponse,
    ProductInfoRequest,
)
from src.core.facet_inference import (
    FacetDefinition,
    FacetInferenceService,
    ProductInfo,
)


def facet_inference_router(
    service: FacetInferenceService = Depends(FacetInferenceService),
) -> APIRouter:
    """Create router for facet inference endpoints."""

    router = APIRouter(prefix="/facet-inference", tags=["facet-inference"])

    @router.post("/predict", response_model=FacetPredictionResponse)
    async def predict_facet(
        product: ProductInfoRequest,
        facet: FacetDefinitionRequest,
    ) -> FacetPredictionResponse:
        """
        Predict labels for a single product facet.

        Args:
            product: Product information
            facet: Facet definition and rules

        Returns:
            Prediction result with labels and confidence
        """
        product_info = ProductInfo(**product.model_dump())
        facet_def = FacetDefinition(**facet.model_dump())

        prediction = await service.predict_facet(
            product=product_info,
            facet=facet_def,
        )

        return FacetPredictionResponse(prediction=prediction)

    @router.post("/predict-multiple", response_model=FacetPredictionsResponse)
    async def predict_multiple_facets(
        product: ProductInfoRequest,
        facets: Sequence[FacetDefinitionRequest],
    ) -> FacetPredictionsResponse:
        """
        Predict labels for multiple product facets concurrently.

        Args:
            product: Product information
            facets: List of facet definitions and rules

        Returns:
            List of prediction results with labels and confidence
        """
        product_info = ProductInfo(**product.model_dump())
        facet_defs = [FacetDefinition(**f.model_dump()) for f in facets]

        predictions = await service.predict_multiple_facets(
            product=product_info,
            facets=facet_defs,
        )

        return FacetPredictionsResponse(predictions=predictions)

    return router
