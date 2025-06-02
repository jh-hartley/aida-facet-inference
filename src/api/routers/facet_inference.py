from fastapi import APIRouter

from src.api.dto.facet_inference import (
    FacetPredictionsResponse,
)
from src.core.facet_inference.service import FacetInferenceService


def facet_inference_router() -> APIRouter:
    router = APIRouter(prefix="/facet-inference", tags=["facet-inference"])

    @router.post(
        "/predict/{product_key}", response_model=FacetPredictionsResponse
    )
    async def predict_attribute(product_key: str) -> FacetPredictionsResponse:
        """
        Predict values for all missing attributes of a product.

        Args:
            product_key: The product key to predict for
        """
        service = FacetInferenceService()
        predictions = await service.predict_for_product_key(product_key)
        return FacetPredictionsResponse(predictions=predictions)

    return router
