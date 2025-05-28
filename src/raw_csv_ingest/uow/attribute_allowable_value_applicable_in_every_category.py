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
        
        if repo.find_by_attribute_key_and_value(attribute_key, value) is not None:
            return None

        attribute_allowable_value = RawAttributeAllowableValueApplicableInEveryCategory(
            attribute_key=attribute_key,
            value=value,
        )

        return repo.create(attribute_allowable_value) 