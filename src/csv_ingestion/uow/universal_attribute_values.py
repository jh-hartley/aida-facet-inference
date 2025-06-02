from src.common.db import db_session
from src.csv_ingestion.records import (
    RawAttributeAllowableValueApplicableInEveryCategoryRecord,
)
from src.csv_ingestion.repositories import (
    RawAttributeAllowableValueApplicableInEveryCategoryRepository,
)


def create_attribute_allowable_value_applicable_in_every_category(
    attribute_key: str,
    value: str,
) -> RawAttributeAllowableValueApplicableInEveryCategoryRecord | None:
    """Create a new globally applicable attribute value if it doesn't exist"""
    with db_session().begin() as session:
        repo = RawAttributeAllowableValueApplicableInEveryCategoryRepository(
            session
        )

        if repo.find_by_attribute_key_and_value(attribute_key, value):
            return None

        record = RawAttributeAllowableValueApplicableInEveryCategoryRecord(
            attribute_key=attribute_key,
            value=value,
        )
        return repo.create(record)
