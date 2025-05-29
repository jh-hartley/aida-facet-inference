from dataclasses import dataclass
from datetime import datetime
from typing import List
from pydantic import BaseModel

from src.raw_csv_ingest.types import (
    RawProductBase,
    RawCategoryBase,
    RawAttributeBase,
    RawProductAttributeValueBase,
    RawRichTextSourceBase
)

@dataclass
class ProductAttribute:
    attribute_key: str
    system_name: str
    friendly_name: str
    value: str
    unit_type: str | None = None

@dataclass
class ProductCategory:
    category_key: str
    system_name: str
    friendly_name: str

@dataclass
class ProductRichText:
    name: str
    content: str
    priority: int
    created_at: datetime

class ProductDetails(BaseModel):
    """Complete product information including all related data"""
    product: RawProductBase
    categories: List[RawCategoryBase]
    attributes: List[RawProductAttributeValueBase]
    rich_texts: List[RawRichTextSourceBase] 