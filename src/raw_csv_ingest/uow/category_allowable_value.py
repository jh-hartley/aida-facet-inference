from src.db.connection import db_session
from src.raw_csv_ingest.models import RawCategoryAllowableValue
from src.raw_csv_ingest.repositories import RawCategoryAllowableValueRepository


def create_category_allowable_value(
    category_key: str,
    attribute_key: str,
    value: str,
) -> RawCategoryAllowableValue | None:
    """Create a new category allowable value if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawCategoryAllowableValueRepository(session)
        
        # Check if value already exists
        existing = repo.find_by_category_key(category_key)
        if any(caav.attribute_key == attribute_key and caav.value == value for caav in existing):
            return None

        category_allowable_value = RawCategoryAllowableValue(
            category_key=category_key,
            attribute_key=attribute_key,
            value=value,
        )

        return repo.create(category_allowable_value) 