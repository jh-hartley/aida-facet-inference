from src.db.connection import db_session
from src.raw_csv_ingestion.records import RawProductRecord
from src.raw_csv_ingestion.repositories import RawProductRepository


def create_product(
    product_key: str,
    system_name: str,
    friendly_name: str,
) -> RawProductRecord | None:
    """Create a new product if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawProductRepository(session)

        if repo.find_by_system_name(system_name):
            return None

        product = RawProductRecord(
            product_key=product_key,
            system_name=system_name,
            friendly_name=friendly_name,
        )

        return repo.create(product)
