from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.models import ProductDetails, ProductGaps
from src.core.types import (
    ProductAttributeGap,
    ProductAttributeValue,
    ProductDescriptor,
)
from src.raw_csv_ingestion.records import (
    RawAttributeAllowableValueApplicableInEveryCategoryRecord,
    RawAttributeAllowableValueInAnyCategoryRecord,
    RawAttributeRecord,
    RawCategoryAllowableValueRecord,
    RawCategoryRecord,
    RawProductAttributeValueRecord,
    RawProductCategoryRecord,
    RawRichTextSourceRecord,
    RawProductAttributeGapRecord,
    RawRecommendationRecord,
)
from src.raw_csv_ingestion.repositories import (
    RawAttributeRepository,
    RawCategoryAllowableValueRepository,
    RawCategoryRepository,
    RawProductAttributeGapRepository,
    RawProductAttributeValueRepository,
    RawProductCategoryRepository,
    RawProductRepository,
    RawRichTextSourceRepository,
)

# Type aliases for long record names
GloballyAllowedValueRecord = (
    RawAttributeAllowableValueApplicableInEveryCategoryRecord
)
SharedAllowedValueRecord = RawAttributeAllowableValueInAnyCategoryRecord


class FacetIdentificationRepository:
    """
    Repository for retrieving complete product information in domain model
    format
    """

    def __init__(self, session: Session):
        self.session = session
        self.product_repo = RawProductRepository(session)
        self.category_repo = RawCategoryRepository(session)
        self.attribute_repo = RawAttributeRepository(session)
        self.product_category_repo = RawProductCategoryRepository(session)
        self.product_attribute_value_repo = RawProductAttributeValueRepository(
            session
        )
        self.rich_text_repo = RawRichTextSourceRepository(session)
        self.product_attribute_gap_repo = RawProductAttributeGapRepository(
            session
        )
        self.category_allowable_value_repo = (
            RawCategoryAllowableValueRepository(session)
        )

    def _get_allowable_values_for_attribute(
        self, category_keys: list[str], attribute_key: str
    ) -> set[str]:
        """Get all allowable values for an attribute across categories"""
        category_values = set(
            av.value
            for av in self.session.scalars(
                select(RawCategoryAllowableValueRecord).where(
                    RawCategoryAllowableValueRecord.category_key.in_(
                        category_keys
                    ),
                    RawCategoryAllowableValueRecord.attribute_key
                    == attribute_key,
                )
            ).all()
        )

        global_values = set(
            av.value
            for av in self.session.scalars(
                select(GloballyAllowedValueRecord).where(
                    GloballyAllowedValueRecord.attribute_key == attribute_key
                )
            ).all()
        )

        any_category_values = set(
            av.value
            for av in self.session.scalars(
                select(SharedAllowedValueRecord).where(
                    SharedAllowedValueRecord.attribute_key == attribute_key
                )
            ).all()
        )

        return category_values | global_values | any_category_values

    def get_product_details(self, product_key: str) -> ProductDetails:
        """
        Get complete information about a product including categories,
        attributes, and rich text in a format suitable for LLM consumption
        """
        product = self.product_repo.get_by_id(product_key)

        categories = [
            cat.friendly_name
            for cat in self.session.scalars(
                select(RawCategoryRecord)
                .join(
                    RawProductCategoryRecord,
                    RawCategoryRecord.category_key
                    == RawProductCategoryRecord.category_key,
                )
                .where(RawProductCategoryRecord.product_key == product_key)
            ).all()
        ]

        attributes = [
            ProductAttributeValue(
                attribute=attr.friendly_name, value=val.value
            )
            for attr, val in self.session.execute(
                select(RawAttributeRecord, RawProductAttributeValueRecord)
                .join(
                    RawProductAttributeValueRecord,
                    RawAttributeRecord.attribute_key
                    == RawProductAttributeValueRecord.attribute_key,
                )
                .where(
                    RawProductAttributeValueRecord.product_key == product_key
                )
            ).all()
        ]

        descriptions = [
            ProductDescriptor(descriptor=rt.name, value=rt.content)
            for rt in self.session.scalars(
                select(RawRichTextSourceRecord)
                .where(RawRichTextSourceRecord.product_key == product_key)
                .order_by(RawRichTextSourceRecord.priority)
            ).all()
        ]

        return ProductDetails(
            product_code=product.product_key,
            product_name=product.friendly_name,
            product_description=descriptions,
            categories=categories,
            attributes=attributes,
        )

    def find_product_details(self, product_key: str) -> ProductDetails | None:
        """
        Find complete information about a product including categories,
        attributes, and rich text in a format suitable for LLM consumption
        """
        try:
            return self.get_product_details(product_key)
        except ValueError:
            return None

    def get_product_gaps(self, product_key: str) -> ProductGaps:
        """
        Get all attributes a product is missing and their possible values
        in an object suitable for LLM consumption
        """
        product = self.product_repo.get_by_id(product_key)

        product_categories = self.product_category_repo.get_by_product_key(
            product_key
        )
        category_keys = [pc.category_key for pc in product_categories]

        gaps = self.product_attribute_gap_repo.get_by_product_key(product_key)

        gap_details = []
        for gap in gaps:
            allowable_values = self._get_allowable_values_for_attribute(
                category_keys, gap.attribute_key
            )

            if allowable_values:
                attribute = self.attribute_repo.get_by_id(gap.attribute_key)
                gap_details.append(
                    ProductAttributeGap(
                        attribute=attribute.friendly_name,
                        allowable_values=sorted(allowable_values),
                    )
                )

        return ProductGaps(
            product_code=product.product_key,
            product_name=product.friendly_name,
            gaps=gap_details,
        )

    def find_product_gaps(self, product_key: str) -> ProductGaps | None:
        """
        Find information about missing attribute values for a product and their
        possible values based on category rules.
        """
        try:
            return self.get_product_gaps(product_key)
        except ValueError:
            return None

    def get_products_with_gaps(self) -> list[str]:
        """
        Get a list of all product keys that have at least one attribute gap.
        """
        return list(
            self.session.scalars(
                select(RawProductAttributeGapRecord.product_key).distinct()
            ).all()
        )

    def get_product_gaps_with_ground_truth(
        self, product_key: str
    ) -> list[tuple[ProductAttributeGap, str | None]]:
        """
        Get all gaps for a product along with their ground truth values from
        recommendations.

        Returns:
            A list of tuples containing (gap, ground_truth_value). The ground
            truth value will be None if no recommendation exists.
        """
        gaps = self.get_product_gaps(product_key)
        recommendations = self.session.scalars(
            select(RawRecommendationRecord).where(
                RawRecommendationRecord.product_key == product_key
            )
        ).all()

        # Create a lookup of recommendations by attribute key
        recommendation_lookup = {
            rec.attribute_key: rec.value for rec in recommendations
        }

        # Match gaps with their ground truth values
        return [
            (
                gap,
                recommendation_lookup.get(
                    self.attribute_repo.get_by_friendly_name(gap.attribute).attribute_key
                ),
            )
            for gap in gaps.gaps
        ]
