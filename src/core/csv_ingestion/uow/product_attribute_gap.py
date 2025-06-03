from src.common.db import db_session
from src.core.infrastructure.database.input_data.records import (
    RawProductAttributeGapRecord,
)
from src.core.infrastructure.database.input_data.repositories import (
    RawProductAttributeGapRepository,
)


def create_product_attribute_gap(
    product_key: str,
    attribute_key: str,
) -> RawProductAttributeGapRecord | None:
    """Create a new product attribute gap if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawProductAttributeGapRepository(session)

        if (
            repo.find_by_product_key_and_attribute_key(
                product_key, attribute_key
            )
            is not None
        ):
            return None

        product_attribute_gap = RawProductAttributeGapRecord(
            product_key=product_key,
            attribute_key=attribute_key,
        )

        return repo.create(product_attribute_gap)
