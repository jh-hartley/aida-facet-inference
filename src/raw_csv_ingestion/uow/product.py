from src.db.connection import db_session
from src.raw_csv_ingestion.records import RawProductRecord
from src.raw_csv_ingestion.repositories import RawProductRepository
from src.raw_csv_ingestion.code_types import process_code_type


def create_product(
    product_key: str,
    system_name: str,
    friendly_name: str,
    code_type: str | None = None,
) -> RawProductRecord | None:
    """
    Create a new product if it doesn't already exist.
    
    Args:
        product_key: Unique identifier for the product
        system_name: System name/code for the product
        friendly_name: Human-readable name for the product
        code_type: Optional explicit code type to use instead of auto-detection
    """
    with db_session().begin() as session:
        repo = RawProductRepository(session)

        if repo.find_by_system_name(system_name):
            return None

        product = RawProductRecord(
            product_key=product_key,
            system_name=system_name,
            friendly_name=friendly_name,
            code_type=process_code_type(system_name, code_type),
        )

        return repo.create(product)
