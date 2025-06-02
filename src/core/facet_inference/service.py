from asyncio import Semaphore, gather
from typing import Sequence, cast

from sqlalchemy.orm import Session

from src.core.facet_inference.inference import ProductFacetPredictor
from src.core.facet_inference.models import FacetPrediction
from src.core.repositories import FacetIdentificationRepository
from src.core.types import ProductAttributeGap
from src.db.connection import SessionLocal


class FacetInferenceService:
    """Service layer for facet inference operations."""

    def __init__(
        self,
        repository: FacetIdentificationRepository | None = None,
        max_concurrent: int = 32,
    ) -> None:
        session = cast(Session, SessionLocal())
        self.repository = repository or FacetIdentificationRepository(session)
        self.max_concurrent = max_concurrent
        self._predictor: ProductFacetPredictor | None = None

    @classmethod
    def from_session(
        cls, session: Session | None = None, max_concurrent: int = 8
    ) -> "FacetInferenceService":
        """
        Create a service instance from a session.
        """
        if session is None:
            session = cast(Session, SessionLocal())
        repository = FacetIdentificationRepository(session)
        return cls(repository=repository, max_concurrent=max_concurrent)

    async def predict_for_product_key(
        self, product_key: str
    ) -> list[FacetPrediction]:
        """
        Predict all missing attributes for a product, managing concurrency
        and prompt logic internally.
        """
        product_details = self.repository.get_product_details(product_key)
        product_gaps = self.repository.get_product_gaps(product_key)
        self._predictor = ProductFacetPredictor(product_details, product_gaps)
        semaphore = Semaphore(self.max_concurrent)

        async def limited_predict(gap: ProductAttributeGap) -> FacetPrediction:
            async with semaphore:
                return await self.predict_attribute(gap)

        tasks = [limited_predict(gap) for gap in product_gaps.gaps]
        predictions = await gather(*tasks)
        return list(predictions)

    async def predict_attribute(
        self,
        gap: ProductAttributeGap,
    ) -> FacetPrediction:
        if self._predictor is None:
            raise RuntimeError(
                "Predictor not initialised. Call predict_for_product_key "
                "first."
            )
        return await self._predictor.apredict_single_gap(gap)

    async def predict_multiple_attributes(
        self,
        gaps: Sequence[ProductAttributeGap],
    ) -> list[FacetPrediction]:
        predictions = await gather(
            *(self.predict_attribute(gap) for gap in gaps)
        )
        return list(predictions)
