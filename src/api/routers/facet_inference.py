from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dto.facet_inference import FacetPredictionsResponse
from src.common.db import get_db
from src.core.facet_inference.service import FacetInferenceService


def facet_inference_router() -> APIRouter:
    router = APIRouter(prefix="/facet-inference", tags=["facet-inference"])

    @router.post(
        "/predict/{product_key}", response_model=FacetPredictionsResponse
    )
    async def predict_attributes_for_product(
        product_key: str,
        db: Session = Depends(get_db)
    ) -> FacetPredictionsResponse:
        """Predict values for all missing attributes of a product."""
        service = FacetInferenceService.from_session(db)
        predictions = await service.predict_for_product_key(product_key)
        return FacetPredictionsResponse(predictions=list(predictions))

    return router
