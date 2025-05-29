from pydantic import BaseModel

from raw_csv_ingest.models import (
    RawProduct,
    RawCategory,
    RawProductAttributeValue,
    RawRichTextSource
)


class ProductDetails(BaseModel):
    """Complete product information including all related data"""
    product: RawProduct
    categories: list[RawCategory]
    attributes: list[RawProductAttributeValue]
    rich_texts: list[RawRichTextSource] 