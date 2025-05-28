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
        
        # Check if value already exists
        existing = repo.find_by_attribute_key(attribute_key)
        if any(aav.attribute_key == attribute_key and aav.value == value for aav in existing):
            return None

        attribute_allowable_value = RawAttributeAllowableValueInAnyCategory(
            attribute_key=attribute_key,
            value=value,
        )

        return repo.create(attribute_allowable_value) 