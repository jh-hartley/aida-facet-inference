from src.db.connection import db_session
from src.raw_csv_ingest.models import RawAttributeAllowableValueInAnyCategory
from src.raw_csv_ingest.repositories import RawAttributeAllowableValueInAnyCategoryRepository


def create_attribute_allowable_value_in_any_category(
    attribute_key: str,
    value: str,
) -> RawAttributeAllowableValueInAnyCategory | None:
    """Create a new attribute allowable value in any category if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawAttributeAllowableValueInAnyCategoryRepository(session)
        
        if repo.find_by_attribute_key_and_value(attribute_key, value) is not None:
            return None

        attribute_allowable_value = RawAttributeAllowableValueInAnyCategory(
            attribute_key=attribute_key,
            value=value,
        )

        return repo.create(attribute_allowable_value) 