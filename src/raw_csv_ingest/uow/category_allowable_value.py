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

        if (
            repo.find_by_category_key_and_attribute_key_and_value(
                category_key, attribute_key, value
            )
            is not None
        ):
            return None

        category_allowable_value = RawCategoryAllowableValue(
            category_key=category_key,
            attribute_key=attribute_key,
            value=value,
        )

        return repo.create(category_allowable_value)
