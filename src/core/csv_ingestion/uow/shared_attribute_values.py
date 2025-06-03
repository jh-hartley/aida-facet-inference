from src.common.db import db_session
from src.core.infrastructure.database.input_data.records import (
    RawAttributeAllowableValueInAnyCategoryRecord,
)
from src.core.infrastructure.database.input_data.repositories import (
    RawAttributeAllowableValueInAnyCategoryRepository,
)


def create_attribute_allowable_value_in_any_category(
    attribute_key: str,
    value: str,
) -> RawAttributeAllowableValueInAnyCategoryRecord | None:
    """Create a new generally available attribute value if it doesn't exist"""
    with db_session().begin() as session:
        repo = RawAttributeAllowableValueInAnyCategoryRepository(session)

        if repo.find_by_attribute_key_and_value(attribute_key, value):
            return None

        record = RawAttributeAllowableValueInAnyCategoryRecord(
            attribute_key=attribute_key,
            value=value,
        )
        return repo.create(record)
