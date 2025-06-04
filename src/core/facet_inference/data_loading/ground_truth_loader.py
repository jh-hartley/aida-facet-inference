"""Loader for ground truth data from human recommendations."""

from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.domain.repositories import FacetIdentificationRepository
from src.core.infrastructure.database.input_data.records import (
    HumanRecommendationRecord,
    RawAttributeRecord,
    RawProductRecord,
)
from src.core.infrastructure.database.input_data.repositories import (
    RawAttributeRepository,
    RawProductRepository,
)


@dataclass
class GroundTruthEntry:
    """Represents a single ground truth entry."""

    product_key: str
    product_system_name: str
    attribute_key: str
    attribute_system_name: str
    attribute_name: str
    value: str
    recommendation_id: str
    action: str


class GroundTruthLoader:
    """Loads and structures ground truth data from human recommendations."""

    def __init__(self, session: Session):
        """Initialize the loader.

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.facet_repo = FacetIdentificationRepository(session)
        self.product_repo = RawProductRepository(session)
        self.attribute_repo = RawAttributeRepository(session)

    def load_ground_truth(self) -> Sequence[GroundTruthEntry]:
        """Load all ground truth data from recommendations.

        Returns:
            Sequence of ground truth entries
        """
        # Get all recommendations except those with "Action"
        recommendations = self.session.scalars(
            select(HumanRecommendationRecord).where(
                HumanRecommendationRecord.action != "Action"
            )
        ).all()

        entries = []
        for rec in recommendations:
            # Get product details
            product = self.session.scalars(
                select(RawProductRecord).where(
                    RawProductRecord.system_name == rec.product_reference
                )
            ).first()
            if not product:
                continue

            # Get attribute details
            attribute = self.session.scalars(
                select(RawAttributeRecord).where(
                    RawAttributeRecord.system_name == rec.attribute_reference
                )
            ).first()
            if not attribute:
                continue

            # Determine ground truth value based on action
            if rec.action == "Make no change":
                value = ""
            elif rec.action == "Apply override":
                value = rec.override
            elif rec.action == "Accept Recommendation":
                value = rec.recommendation
            else:
                continue  # Skip unknown action types

            entries.append(
                GroundTruthEntry(
                    product_key=product.product_key,
                    product_system_name=product.system_name,
                    attribute_key=attribute.attribute_key,
                    attribute_system_name=attribute.system_name,
                    attribute_name=rec.attribute_name,
                    value=value,
                    recommendation_id=str(rec.id),
                    action=rec.action,
                )
            )

        return entries

    def get_entries_by_product(
        self, product_key: str
    ) -> Sequence[GroundTruthEntry]:
        """Get ground truth entries for a specific product.

        Args:
            product_key: Product key to filter by

        Returns:
            Sequence of ground truth entries for the product
        """
        product = self.product_repo.get_by_id(product_key)
        if not product:
            return []

        return [
            entry
            for entry in self.load_ground_truth()
            if entry.product_key == product_key
        ]

    def get_entries_by_attribute(
        self, attribute_key: str
    ) -> Sequence[GroundTruthEntry]:
        """Get ground truth entries for a specific attribute.

        Args:
            attribute_key: Attribute key to filter by

        Returns:
            Sequence of ground truth entries for the attribute
        """
        attribute = self.attribute_repo.get_by_id(attribute_key)
        if not attribute:
            return []

        return [
            entry
            for entry in self.load_ground_truth()
            if entry.attribute_key == attribute_key
        ]

    def get_unique_product_keys(self) -> set[str]:
        """Get all unique product keys in the ground truth data.

        Returns:
            Set of product keys
        """
        return {entry.product_key for entry in self.load_ground_truth()}

    def get_unique_attribute_keys(self) -> set[str]:
        """Get all unique attribute keys in the ground truth data.

        Returns:
            Set of attribute keys
        """
        return {entry.attribute_key for entry in self.load_ground_truth()}
