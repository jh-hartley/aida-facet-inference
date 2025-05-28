from src.db.connection import db_session
from src.raw_csv_ingest.models import RawProductCategory
from src.raw_csv_ingest.repositories import RawProductCategoryRepository


def create_product_category(
    product_key: str,
    category_key: str,
) -> RawProductCategory | None:
    """Create a new product-category relationship if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawProductCategoryRepository(session)
        
        # Check if relationship already exists
        existing = repo.find_by_product_key(product_key)
        if any(pc.category_key == category_key for pc in existing):
            return None

        product_category = RawProductCategory(
            product_key=product_key,
            category_key=category_key,
        )

        return repo.create(product_category) 