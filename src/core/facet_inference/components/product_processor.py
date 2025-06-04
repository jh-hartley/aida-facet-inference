"""Processes products for facet inference."""

import logging
from typing import Mapping, Sequence, Tuple

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from src.core.domain.models import FacetPrediction
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.domain.types import ProductAttributeGap
from src.core.facet_inference.data_loading.ground_truth_loader import (
    GroundTruthEntry,
    GroundTruthLoader,
)
from src.core.facet_inference.service import FacetInferenceService
from src.core.infrastructure.database.input_data.records import (
    RawAttributeRecord,
    RawProductRecord,
)

logger = logging.getLogger(__name__)


class ProductProcessor:
    """Processes products for facet inference."""

    def __init__(self, session: Session):
        """Initialize the processor.

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.repository = FacetIdentificationRepository(session)
        self.ground_truth_loader = GroundTruthLoader(session)
        self.service = FacetInferenceService.from_session(session)

    def get_accepted_recommendations(
        self,
    ) -> Mapping[str, Sequence[GroundTruthEntry]]:
        """Get all accepted recommendations grouped by product reference.

        Returns:
            Dict mapping product references to their recommendations
        """
        entries = self.ground_truth_loader.load_ground_truth()

        product_recommendations: dict[str, list[GroundTruthEntry]] = {}
        for entry in entries:
            if entry.product_system_name not in product_recommendations:
                product_recommendations[entry.product_system_name] = []
            product_recommendations[entry.product_system_name].append(entry)

        return product_recommendations

    def get_product_key_from_system_name(self, system_name: str) -> str | None:
        """Get product key from system name."""
        product = self.session.scalars(
            select(RawProductRecord).where(
                RawProductRecord.system_name == system_name
            )
        ).first()
        return product.product_key if product else None

    def get_attribute_key_from_system_name(
        self, system_name: str
    ) -> str | None:
        """Get attribute key from system name."""
        attribute = self.session.scalars(
            select(RawAttributeRecord).where(
                RawAttributeRecord.system_name == system_name
            )
        ).first()
        return attribute.attribute_key if attribute else None

    def get_allowable_values(self, attribute_key: str) -> list[str]:
        """Get allowable values for an attribute."""
        category_values = list(
            self.session.scalars(
                select(text("value"))
                .select_from(text("raw_category_allowable_values"))
                .where(text("attribute_key = :attribute_key"))
                .params(attribute_key=attribute_key)
            ).all()
        )

        global_values = list(
            self.session.scalars(
                select(text("value"))
                .select_from(
                    text(
                        "raw_attribute_allowable_values_"
                        "applicable_in_every_category"
                    )
                )
                .where(text("attribute_key = :attribute_key"))
                .params(attribute_key=attribute_key)
            ).all()
        )

        any_category_values = list(
            self.session.scalars(
                select(text("value"))
                .select_from(
                    text("raw_attribute_allowable_values_in_any_category")
                )
                .where(text("attribute_key = :attribute_key"))
                .params(attribute_key=attribute_key)
            ).all()
        )

        return sorted(
            list(set(category_values + global_values + any_category_values))
        )

    async def process_product(
        self, product_ref: str, recommendations: Sequence[GroundTruthEntry]
    ) -> Tuple[str | None, Sequence[FacetPrediction]]:
        """Process a product and generate predictions.

        Args:
            product_ref: Product reference (system name)
            recommendations: Sequence of ground truth entries for the product

        Returns:
            Tuple of (product_key, predictions)
        """
        if not recommendations:
            logger.error(f"No recommendations found for product {product_ref}")
            return None, []

        product_key = recommendations[0].product_key

        product_categories = (
            self.service.repository.product_category_repo.get_by_product_key(
                product_key
            )
        )
        category_keys = [pc.category_key for pc in product_categories]

        gaps = []
        seen_attributes = set()

        for rec in recommendations:
            if rec.attribute_name in seen_attributes:
                continue

            allowable_values = list(
                self.service.repository._get_allowable_values_for_attribute(
                    category_keys, rec.attribute_key
                )
            )

            gaps.append(
                ProductAttributeGap(
                    attribute=rec.attribute_name,
                    allowable_values=allowable_values,
                )
            )
            seen_attributes.add(rec.attribute_name)
            logger.info(
                f"Added gap for attribute {rec.attribute_name} "
                f"with {len(allowable_values)} allowable values"
            )

        if not gaps:
            logger.warning(f"No valid gaps found for product {product_key}")
            return product_key, []

        predictions = await self.service.predict_specific_gaps(
            product_key, gaps
        )
        logger.info(f"Generated {len(predictions)} predictions")

        return product_key, predictions
