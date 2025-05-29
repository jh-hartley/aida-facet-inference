from sqlalchemy.orm import Session

from src.core.models import ProductDetails, ProductGaps
from src.core.types import (
    ProductAttributeGap,
    ProductAttributeValue,
    ProductDescriptor,
)
from src.raw_csv_ingest.repositories import (
    RawAttributeRepository,
    RawCategoryAllowableValueRepository,
    RawCategoryRepository,
    RawProductAttributeAllowableValueRepository,
    RawProductAttributeGapRepository,
    RawProductAttributeValueRepository,
    RawProductCategoryRepository,
    RawProductRepository,
    RawRichTextSourceRepository,
)


class ProductRepository:
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
        self.product_attribute_gap_repo = RawProductAttributeGapRepository(
            session
        )
        self.product_attribute_allowable_value_repo = (
            RawProductAttributeAllowableValueRepository(session)
        )

    def get_product_details(self, product_key: str) -> ProductDetails:
        """
        Get complete information about a product including categories,
        attributes, and rich text in a format suitable for LLM consumption
        """
        product = self.product_repo.get_by_id(product_key)

        product_categories = self.product_category_repo.find_by_product_key(
            product_key
        )
        categories = [
            c.friendly_name
            for pc in product_categories
            if (c := self.category_repo.find_by_id(pc.category_key))
        ]

        attribute_values = (
            self.product_attribute_value_repo.find_by_product_key(product_key)
        )
        attributes = []
        for av in attribute_values:
            if attribute := self.attribute_repo.find_by_id(av.attribute_key):
                attributes.append(
                    ProductAttributeValue(
                        attribute=attribute.friendly_name, value=av.value
                    )
                )

        rich_texts = self.rich_text_repo.find_by_product_key(product_key)
        descriptions = [
            ProductDescriptor(descriptor=rt.name, value=rt.content)
            for rt in rich_texts
        ]

        return ProductDetails(
            product_code=product.system_name,
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
        """
        product = self.product_repo.get_by_id(product_key)

        gaps = self.product_attribute_gap_repo.find_by_product_key(product_key)

        attribute_gaps = []
        for gap in gaps:
            if attribute := self.attribute_repo.find_by_id(gap.attribute_key):
                # fmt: off
                allowable_values = (
                    self.product_attribute_allowable_value_repo
                    .find_by_product_key_and_attribute_key(
                        product_key,
                        gap.attribute_key,
                    )
                )
                # fmt: on

                if allowable_values:
                    attribute_gaps.append(
                        ProductAttributeGap(
                            attribute=attribute.friendly_name,
                            allowable_values=[
                                av.value for av in allowable_values
                            ],
                        )
                    )

        return ProductGaps(
            product_code=product.system_name,
            product_name=product.friendly_name,
            gaps=attribute_gaps,
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
