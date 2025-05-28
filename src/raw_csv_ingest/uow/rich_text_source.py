from src.db.connection import db_session
from src.raw_csv_ingest.models import RawRichTextSource
from src.raw_csv_ingest.repositories import RawRichTextSourceRepository


def create_rich_text_source(
    product_key: str,
    attribute_key: str,
    source: str,
) -> RawRichTextSource | None:
    """Create a new rich text source if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawRichTextSourceRepository(session)
        
        # Replace inefficient O(N) check with direct database query
        if repo.find_by_product_key_and_attribute_key_and_source(product_key, attribute_key, source) is not None:
            return None

        rich_text_source = RawRichTextSource(
            product_key=product_key,
            attribute_key=attribute_key,
            source=source,
        )

        return repo.create(rich_text_source) 