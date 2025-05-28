from src.db.connection import db_session
from src.raw_csv_ingest.models import RawAttribute
from src.raw_csv_ingest.repositories import RawAttributeRepository


def create_attribute(
    attribute_key: str,
    system_name: str,
    friendly_name: str,
    attribute_type: str,
    unit_measure_type: str,
) -> RawAttribute | None:
    """Create a new attribute if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawAttributeRepository(session)
        
        if repo.find_by_system_name(system_name):
            return None

        attribute = RawAttribute(
            attribute_key=attribute_key,
            system_name=system_name,
            friendly_name=friendly_name,
            attribute_type=attribute_type,
            unit_measure_type=unit_measure_type,
        )

        return repo.create(attribute) 