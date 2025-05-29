from sqlalchemy.orm import Session

from raw_csv_ingest.models import (
    RawProduct,
    RawCategory,
    RawAttribute,
    RawProductAttributeValue,
    RawRichTextSource
)
from src.raw_csv_ingest.repositories import (
    RawProductRepository,
    RawCategoryRepository,
    RawAttributeRepository,
    RawProductCategoryRepository,
    RawProductAttributeValueRepository,
    RawRichTextSourceRepository
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
        self.product_attribute_value_repo = RawProductAttributeValueRepository(session)
        self.rich_text_repo = RawRichTextSourceRepository(session)

    def get_product_details(self, product_key: str) -> dict:
        """
        Get complete information about a product including categories, 
        attributes, and rich text
        """
        product = self.product_repo.get_by_id(product_key)

        product_categories = self.product_category_repo.find_by_product_key(product_key)
        categories = [
            RawCategory(
                category_key=c.category_key,
                system_name=c.system_name,
                friendly_name=c.friendly_name
            )
            for pc in product_categories
            if (c := self.category_repo.find_by_id(pc.category_key))
        ]

        attribute_values = self.product_attribute_value_repo.find_by_product_key(product_key)
        attributes = []
        for av in attribute_values:
            if attribute := self.attribute_repo.find_by_id(av.attribute_key):
                attributes.append(
                    RawProductAttributeValue(
                        product_key=product_key,
                        attribute_key=attribute.attribute_key,
                        value=av.value
                    )
                )

        rich_texts = [
            RawRichTextSource(
                source_key=rt.source_key,
                product_key=product_key,
                content=rt.content,
                name=rt.name,
                priority=rt.priority,
                created_at=rt.created_at
            )
            for rt in self.rich_text_repo.find_by_product_key(product_key)
        ]

        return {
            'product': RawProduct(
                product_key=product.product_key,
                system_name=product.system_name,
                friendly_name=product.friendly_name
            ),
            'categories': categories,
            'attributes': attributes,
            'rich_texts': rich_texts
        }

    def find_product_details(self, product_key: str) -> dict | None:
        """
        Find complete information about a product including categories, 
        attributes, and rich text
        """
        try:
            return self.get_product_details(product_key)
        except ValueError:
            return None 