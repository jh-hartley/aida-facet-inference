"""Ground truth data loading and evaluation for facet predictions."""

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


@dataclass
class GroundTruthEntry:
    """A single ground truth entry for a product attribute."""
    product_key: str
    product_system_name: str
    attribute_key: str
    attribute_system_name: str
    ground_truth_value: str


class GroundTruthLoader:
    """Loads and structures ground truth data from human recommendations."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = FacetIdentificationRepository(session)

    def load_ground_truth(self) -> Sequence[GroundTruthEntry]:
        """
        Load all ground truth data from accepted recommendations.
        
        Returns:
            A sequence of GroundTruthEntry objects containing product and attribute
            information along with the ground truth values.
        """
        # Get all accepted recommendations
        recommendations = self.session.scalars(
            select(HumanRecommendationRecord).where(
                HumanRecommendationRecord.action == "Accept Recommendation"
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

            entries.append(
                GroundTruthEntry(
                    product_key=product.product_key,
                    product_system_name=product.system_name,
                    attribute_key=attribute.attribute_key,
                    attribute_system_name=attribute.system_name,
                    ground_truth_value=rec.value,
                )
            )

        return entries

    def get_ground_truth_by_product(
        self, product_key: str
    ) -> Sequence[GroundTruthEntry]:
        """Get ground truth entries for a specific product."""
        return [
            entry
            for entry in self.load_ground_truth()
            if entry.product_key == product_key
        ]

    def get_ground_truth_by_attribute(
        self, attribute_key: str
    ) -> Sequence[GroundTruthEntry]:
        """Get ground truth entries for a specific attribute."""
        return [
            entry
            for entry in self.load_ground_truth()
            if entry.attribute_key == attribute_key
        ]

    def get_unique_products(self) -> set[str]:
        """Get set of unique product keys in ground truth data."""
        return {entry.product_key for entry in self.load_ground_truth()}

    def get_unique_attributes(self) -> set[str]:
        """Get set of unique attribute keys in ground truth data."""
        return {entry.attribute_key for entry in self.load_ground_truth()} 