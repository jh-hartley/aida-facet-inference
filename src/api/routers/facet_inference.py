from typing import Sequence

from fastapi import APIRouter, Depends

from src.api.dto.facet_inference import (
    FacetPredictionResponse,
    FacetPredictionsResponse,
    ProductDetailsRequest,
    ProductGapsRequest,
)
from src.core.facet_inference import FacetInferenceService
from src.core.models import ProductDetails, ProductGaps
from src.core.types import (
    ProductAttributeGap,
    ProductAttributeValue,
    ProductDescriptor,
)


def facet_inference_router(
    service: FacetInferenceService = Depends(FacetInferenceService),
) -> APIRouter:
    """Create router for facet inference endpoints."""

    router = APIRouter(prefix="/facet-inference", tags=["facet-inference"])

    @router.post("/predict", response_model=FacetPredictionResponse)
    async def predict_attribute(
        product: ProductDetailsRequest,
        gap: ProductGapsRequest,
    ) -> FacetPredictionResponse:
        """
        Predict a value for a missing attribute.

        Args:
            product: Complete product information
            gap: Information about the missing attribute and its allowed values

        Returns:
            Prediction result with value and confidence
        """
        # Convert request DTOs to domain models
        product_details = ProductDetails(
            product_key=product.product_key,
            product_code=product.product_code,
            product_name=product.product_name,
            code_type=product.code_type,
            product_description=[
                ProductDescriptor(descriptor=d.descriptor, value=d.value)
                for d in product.product_description
            ],
            categories=product.categories,
            attributes=[
                ProductAttributeValue(attribute=a.attribute, value=a.value)
                for a in product.attributes
            ],
        )

        product_gaps = ProductGaps(
            product_code=gap.product_code,
            product_name=gap.product_name,
            gaps=[
                ProductAttributeGap(
                    attribute=g.attribute,
                    allowable_values=g.allowable_values,
                )
                for g in gap.gaps
            ],
        )

        prediction = await service.predict_attribute(
            product=product_details,
            gap=product_gaps,
        )

        return FacetPredictionResponse(prediction=prediction)

    @router.post("/predict-multiple", response_model=FacetPredictionsResponse)
    async def predict_multiple_attributes(
        product: ProductDetailsRequest,
        gaps: Sequence[ProductGapsRequest],
    ) -> FacetPredictionsResponse:
        """
        Predict values for multiple missing attributes concurrently.

        Args:
            product: Complete product information
            gaps: List of missing attributes and their allowed values

        Returns:
            List of prediction results with values and confidence
        """
        # Convert request DTOs to domain models
        product_details = ProductDetails(
            product_key=product.product_key,
            product_code=product.product_code,
            code_type=product.code_type,
            product_name=product.product_name,
            product_description=[
                ProductDescriptor(descriptor=d.descriptor, value=d.value)
                for d in product.product_description
            ],
            categories=product.categories,
            attributes=[
                ProductAttributeValue(attribute=a.attribute, value=a.value)
                for a in product.attributes
            ],
        )

        product_gaps = [
            ProductGaps(
                product_code=gap.product_code,
                product_name=gap.product_name,
                gaps=[
                    ProductAttributeGap(
                        attribute=g.attribute,
                        allowable_values=g.allowable_values,
                    )
                    for g in gap.gaps
                ],
            )
            for gap in gaps
        ]

        predictions = await service.predict_multiple_attributes(
            product=product_details,
            gaps=product_gaps,
        )

        return FacetPredictionsResponse(predictions=predictions)

    return router
