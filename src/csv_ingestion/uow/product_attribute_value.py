from src.common.db import db_session
from src.csv_ingestion.records import RawProductAttributeValueRecord
from src.csv_ingestion.repositories import (
    RawProductAttributeValueRepository,
)


def create_product_attribute_value(
    product_key: str,
    attribute_key: str,
    value: str,
) -> RawProductAttributeValueRecord | None:
    """Create a new product attribute value if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawProductAttributeValueRepository(session)

        if (
            repo.find_by_product_key_and_attribute_key_and_value(
                product_key, attribute_key, value
            )
            is not None
        ):
            return None

        product_attribute_value = RawProductAttributeValueRecord(
            product_key=product_key,
            attribute_key=attribute_key,
            value=value,
        )

        return repo.create(product_attribute_value)
