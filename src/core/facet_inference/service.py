from typing import Sequence

from sqlalchemy.orm import Session

from src.core.domain.models import FacetPrediction, ProductDetails
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.domain.types import ProductAttributeGap
from src.core.facet_inference.concurrency import AsyncConcurrencyManager
from src.core.facet_inference.inference import ProductFacetPredictor
from src.core.infrastructure.llm.client import Llm
from src.core.infrastructure.llm.models import LlmModel


class FacetInferenceService:
    """Service layer for facet inference operations."""

    def __init__(
        self,
        repository: FacetIdentificationRepository,
        max_concurrent: int = 32,
    ) -> None:
        self.repository = repository
        self.concurrency_manager = AsyncConcurrencyManager(max_concurrent)
        self.llm_client = Llm(LlmModel.GPT_4O_MINI)

    @classmethod
    def from_session(
        cls,
        session: Session,
        max_concurrent: int = 32,
    ) -> "FacetInferenceService":
        """Create a service instance from a session."""
        repository = FacetIdentificationRepository(session)
        return cls(
            repository=repository,
            max_concurrent=max_concurrent,
        )

    async def predict_for_product_key(
        self,
        product_key: str,
        evaluation_mode: bool = False,
    ) -> Sequence[FacetPrediction]:
        """
        Predict all missing attributes for a product. If evaluation_mode is
        True, only predict for attributes that have accepted recommendations.
        Otherwise, predict for all attribute gaps.

        This is largely a method for the demo rather than for production use.
        """
        product_details = self.repository.get_product_details(product_key)

        if evaluation_mode:
            product_gaps = (
                self.repository.get_product_gaps_from_recommendations(
                    product_key
                )
            )
        else:
            product_gaps = self.repository.get_product_gaps(product_key)

        predictor = ProductFacetPredictor(product_details, self.llm_client)
        return await self.concurrency_manager.execute(
            predictor.predict_gap, product_gaps.gaps
        )

    async def predict_specific_gaps(
        self,
        product_key: str,
        gaps: Sequence[ProductAttributeGap],
    ) -> Sequence[FacetPrediction]:
        """
        Predict values for specific attribute values.

        This method is useful for handling specific attribute gaps or
        targeted predictions.
        """
        product_details = self.repository.get_product_details(product_key)
        predictor = ProductFacetPredictor(product_details, self.llm_client)
        return await self.concurrency_manager.execute(
            predictor.predict_gap, gaps
        )

    async def _predict_attribute(
        self,
        gap: ProductAttributeGap,
        product_details: ProductDetails,
    ) -> FacetPrediction:
        """Predict a value for a single attribute."""
        predictor = ProductFacetPredictor(product_details, self.llm_client)
        return await predictor.predict_gap(gap)

    async def _predict_multiple_attributes(
        self,
        gaps: Sequence[ProductAttributeGap],
        product_details: ProductDetails,
    ) -> Sequence[FacetPrediction]:
        """Predict values for multiple attributes concurrently."""
        predictor = ProductFacetPredictor(product_details, self.llm_client)
        return await self.concurrency_manager.execute(
            predictor.predict_gap, gaps
        )
