from src.db.connection import db_session
from src.raw_csv_ingest.models import RawProductAttributeValue
from src.raw_csv_ingest.repositories import RawProductAttributeValueRepository


def create_product_attribute_value(
    product_key: str,
    attribute_key: str,
    value: str,
) -> RawProductAttributeValue | None:
    """Create a new product attribute value if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawProductAttributeValueRepository(session)
        
        # Check if value already exists
        existing = repo.find_by_product_key(product_key)
        if any(pav.attribute_key == attribute_key and pav.value == value for pav in existing):
            return None

        product_attribute_value = RawProductAttributeValue(
            product_key=product_key,
            attribute_key=attribute_key,
            value=value,
        )

        return repo.create(product_attribute_value) 