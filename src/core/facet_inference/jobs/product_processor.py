"""Product processing for facet inference jobs."""

import logging
from collections import defaultdict

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from src.core.domain.models import FacetPrediction
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.domain.types import ProductAttributeGap
from src.core.facet_inference.service import FacetInferenceService
from src.core.infrastructure.database.input_data.records import (
    HumanRecommendationRecord,
    RawAttributeRecord,
    RawProductRecord,
)

logger = logging.getLogger(__name__)


class ProductProcessor:
    """Processes products for facet inference."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = FacetIdentificationRepository(session)
        self.service = FacetInferenceService.from_session(session)

    def get_accepted_recommendations(
        self,
    ) -> dict[str, list[HumanRecommendationRecord]]:
        """
        Get all accepted recommendations grouped by product reference.
        Returns a dict of {product_reference: [recommendations]}
        """
        recommendations = self.session.scalars(
            select(HumanRecommendationRecord).where(
                HumanRecommendationRecord.action == "Accept Recommendation"
            )
        ).all()

        product_recommendations: dict[str, list[HumanRecommendationRecord]] = {}
        for rec in recommendations:
            if rec.product_reference not in product_recommendations:
                product_recommendations[rec.product_reference] = []
            product_recommendations[rec.product_reference].append(rec)

        return product_recommendations

    def get_product_key_from_system_name(self, system_name: str) -> str | None:
        """Get product key from system name."""
        product = self.session.scalars(
            select(RawProductRecord).where(
                RawProductRecord.system_name == system_name
            )
        ).first()
        return product.product_key if product else None

    def get_attribute_key_from_system_name(self, system_name: str) -> str | None:
        """Get attribute key from system name."""
        attribute = self.session.scalars(
            select(RawAttributeRecord).where(
                RawAttributeRecord.system_name == system_name
            )
        ).first()
        return attribute.attribute_key if attribute else None

    def get_allowable_values(self, attribute_key: str) -> list[str]:
        """Get allowable values for an attribute."""
        # Get values from category-specific rules
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

        # Get values from any-category rules
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

        # Combine all values and remove duplicates
        return sorted(
            list(set(category_values + global_values + any_category_values))
        )

    async def process_product(
        self, system_name: str, recommendations: list[HumanRecommendationRecord]
    ) -> tuple[str | None, list[FacetPrediction]]:
        """
        Process a single product and its recommendations.
        
        Returns:
            Tuple of (product_key, predictions) where product_key may be None
            if the product was not found.
        """
        # Get product key from system name
        product_key = self.get_product_key_from_system_name(system_name)
        if not product_key:
            logger.warning(f"No product found for system name: {system_name}")
            return None, []

        logger.info(
            f"Processing product {product_key} ({system_name}) "
            f"with {len(recommendations)} accepted recommendations"
        )

        # Get gaps that have recommendations, deduplicating by attribute name
        attribute_to_gap: dict[str, ProductAttributeGap] = {}
        for rec in recommendations:
            # Get attribute key from system name
            attribute_key = self.get_attribute_key_from_system_name(
                rec.attribute_reference
            )
            if attribute_key:
                # Get attribute details
                attribute = self.session.scalars(
                    select(RawAttributeRecord).where(
                        RawAttributeRecord.attribute_key == attribute_key
                    )
                ).first()

                if attribute:
                    # Only add gap if we haven't seen this attribute before
                    if attribute.friendly_name not in attribute_to_gap:
                        # Get allowable values
                        allowable_values = self.get_allowable_values(attribute_key)

                        attribute_to_gap[attribute.friendly_name] = ProductAttributeGap(
                            attribute=attribute.friendly_name,
                            allowable_values=allowable_values,
                        )
                        logger.info(
                            f"Added gap for attribute {attribute.friendly_name} "
                            f"with {len(allowable_values)} allowable values"
                        )
                else:
                    logger.warning(
                        f"No attribute found for key: {attribute_key}"
                    )
            else:
                logger.warning(
                    f"No attribute found for system name: "
                    f"{rec.attribute_reference}"
                )

        gaps = list(attribute_to_gap.values())
        if not gaps:
            logger.warning(f"No valid gaps found for product {product_key}")
            return product_key, []

        # Process gaps
        predictions = await self.service.predict_specific_gaps(
            product_key, gaps
        )
        logger.info(f"Generated {len(predictions)} predictions")

        return product_key, list(predictions) 