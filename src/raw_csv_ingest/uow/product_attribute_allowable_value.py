from src.db.connection import db_session
from src.raw_csv_ingest.models import RawProductAttributeAllowableValue
from src.raw_csv_ingest.repositories import RawProductAttributeAllowableValueRepository


def create_product_attribute_allowable_value(
    product_key: str,
    attribute_key: str,
    value: str,
) -> RawProductAttributeAllowableValue | None:
    """Create a new product attribute allowable value if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawProductAttributeAllowableValueRepository(session)
        
        if repo.find_by_product_key_and_attribute_key_and_value(product_key, attribute_key, value) is not None:
            return None

        product_attribute_allowable_value = RawProductAttributeAllowableValue(
            product_key=product_key,
            attribute_key=attribute_key,
            value=value,
        )

        return repo.create(product_attribute_allowable_value) 