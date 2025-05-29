from src.db.connection import db_session
from src.raw_csv_ingest.records import RawCategoryRecord
from src.raw_csv_ingest.repositories import RawCategoryRepository


def create_category(
    category_key: str,
    system_name: str,
    friendly_name: str,
) -> RawCategoryRecord | None:
    """Create a new category if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawCategoryRepository(session)

        if repo.find_by_system_name(system_name):
            return None

        category = RawCategoryRecord(
            category_key=category_key,
            system_name=system_name,
            friendly_name=friendly_name,
        )

        return repo.create(category)
