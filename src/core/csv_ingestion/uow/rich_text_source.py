from uuid import uuid4

from src.common.db import db_session
from src.core.infrastructure.database.input_data.records import (
    RawRichTextSourceRecord,
)
from src.core.infrastructure.database.input_data.repositories import (
    RawRichTextSourceRepository,
)


def create_rich_text_source(
    product_key: str,
    content: str,
    name: str,
    priority: int,
) -> RawRichTextSourceRecord | None:
    """Create a new rich text source if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawRichTextSourceRepository(session)

        if repo.find_by_product_key_and_name(product_key, name) is not None:
            return None

        source = RawRichTextSourceRecord(
            source_key=str(uuid4()),
            product_key=product_key,
            content=content,
            name=name,
            priority=priority,
        )

        return repo.create(source)
