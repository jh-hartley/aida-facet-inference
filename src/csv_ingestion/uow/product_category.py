from src.common.db import db_session
from src.csv_ingestion.records import RawProductCategoryRecord
from src.csv_ingestion.repositories import RawProductCategoryRepository


def create_product_category(
    product_key: str,
    category_key: str,
) -> RawProductCategoryRecord | None:
    """Create a new product category if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawProductCategoryRepository(session)

        if (
            repo.find_by_product_key_and_category_key(
                product_key, category_key
            )
            is not None
        ):
            return None

        product_category = RawProductCategoryRecord(
            product_key=product_key,
            category_key=category_key,
        )

        return repo.create(product_category)
