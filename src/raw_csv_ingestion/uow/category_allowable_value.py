from src.db.connection import db_session
from src.raw_csv_ingestion.records import (
    RawCategoryAllowableValueRecord,
    RawCategoryAttributeRecord,
)
from src.raw_csv_ingestion.repositories import (
    RawCategoryAllowableValueRepository,
)


def create_category_allowable_value(
    category_attribute_key: str,
    value: str,
    unit_type: str = "",
    minimum_value: str = "",
    minimum_unit: str = "",
    maximum_value: str = "",
    maximum_unit: str = "",
    range_qualifier: str = "",
) -> RawCategoryAllowableValueRecord | None:
    """Create a new category allowable value if it doesn't already exist"""
    with db_session().begin() as session:
        category_attribute = session.get(
            RawCategoryAttributeRecord, category_attribute_key
        )
        if category_attribute is None:
            return None

        repo = RawCategoryAllowableValueRepository(session)

        if (
            repo.find_by_category_key_and_attribute_key_and_value(
                category_attribute.category_key,
                category_attribute.attribute_key,
                value,
            )
            is not None
        ):
            return None

        # Convert numeric strings to float, empty strings remain empty
        minimum_value_float = (
            float(minimum_value) if minimum_value.strip() else None
        )
        maximum_value_float = (
            float(maximum_value) if maximum_value.strip() else None
        )

        category_allowable_value = RawCategoryAllowableValueRecord(
            category_key=category_attribute.category_key,
            attribute_key=category_attribute.attribute_key,
            value=value,
            unit_type=unit_type.strip(),
            minimum_value=minimum_value_float,
            minimum_unit=minimum_unit.strip(),
            maximum_value=maximum_value_float,
            maximum_unit=maximum_unit.strip(),
            range_qualifier=range_qualifier.strip(),
        )

        return repo.create(category_allowable_value)
