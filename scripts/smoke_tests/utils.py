from typing import Optional

from src.core.repositories import FacetIdentificationRepository
from src.db.connection import SessionLocal


def format_section(title: str, content: str) -> str:
    """Format a section with a title and separator."""
    separator = "=" * 80
    return f"{separator}\n{title}\n{separator}\n\n{content}"


def get_product_key(
    product_key: Optional[str] = None, require_gaps: bool = True
) -> str:
    """
    Get a product key either from the provided argument or from the database.

    Args:
        product_key: Optional product key to use
        require_gaps: If True, will return a product that has gaps.
                     If False, will return a product that has NO gaps.

    Raises:
        ValueError: If no suitable product key is found
    """
    if product_key:
        return product_key

    with SessionLocal() as session:
        repository = FacetIdentificationRepository(session)
        result = repository.get_single_product(with_gaps=require_gaps)

        if not result:
            if require_gaps:
                raise ValueError("No products with gaps found in database")
            else:
                raise ValueError("No products without gaps found in database")

        return result
