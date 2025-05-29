from src.db.connection import db_session
from src.raw_csv_ingestion.records import RawCategoryAttributeRecord
from src.raw_csv_ingestion.repositories import RawCategoryAttributeRepository


def create_category_attribute(
    category_attribute_key: str,
    category_key: str,
    attribute_key: str,
) -> RawCategoryAttributeRecord | None:
    """Create a new category attribute if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawCategoryAttributeRepository(session)

        if repo.find_by_category_key_and_attribute_key(
            category_key, attribute_key
        ):
            return None

        category_attribute = RawCategoryAttributeRecord(
            category_attribute_key=category_attribute_key,
            category_key=category_key,
            attribute_key=attribute_key,
        )

        return repo.create(category_attribute)
