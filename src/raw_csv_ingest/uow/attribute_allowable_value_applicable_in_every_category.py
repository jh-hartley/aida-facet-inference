from src.db.connection import db_session
from src.raw_csv_ingest.models import RawAttributeAllowableValueApplicableInEveryCategory
from src.raw_csv_ingest.repositories import RawAttributeAllowableValueApplicableInEveryCategoryRepository


def create_attribute_allowable_value_applicable_in_every_category(
    attribute_key: str,
    value: str,
) -> RawAttributeAllowableValueApplicableInEveryCategory | None:
    """Create a new attribute allowable value applicable in every category if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawAttributeAllowableValueApplicableInEveryCategoryRepository(session)
        
        # Check if value already exists
        existing = repo.find_by_attribute_key(attribute_key)
        if any(aav.attribute_key == attribute_key and aav.value == value for aav in existing):
            return None

        attribute_allowable_value = RawAttributeAllowableValueApplicableInEveryCategory(
            attribute_key=attribute_key,
            value=value,
        )

        return repo.create(attribute_allowable_value) 