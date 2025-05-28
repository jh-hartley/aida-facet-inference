from src.db.connection import db_session
from src.raw_csv_ingest.models import RawProductAttributeGap
from src.raw_csv_ingest.repositories import RawProductAttributeGapRepository


def create_product_attribute_gap(
    product_key: str,
    attribute_key: str,
) -> RawProductAttributeGap | None:
    """Create a new product attribute gap if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawProductAttributeGapRepository(session)
        
        # Check if gap already exists
        existing = repo.find_by_product_key(product_key)
        if any(pag.attribute_key == attribute_key for pag in existing):
            return None

        product_attribute_gap = RawProductAttributeGap(
            product_key=product_key,
            attribute_key=attribute_key,
        )

        return repo.create(product_attribute_gap) 