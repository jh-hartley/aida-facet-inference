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
        
        # Check if source already exists
        existing = repo.find_by_product_key(product_key)
        if any(rts.attribute_key == attribute_key and rts.source == source for rts in existing):
            return None

        rich_text_source = RawRichTextSource(
            product_key=product_key,
            attribute_key=attribute_key,
            source=source,
        )

        return repo.create(rich_text_source) 