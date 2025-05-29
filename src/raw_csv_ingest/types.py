from datetime import datetime
from pydantic import BaseModel, Field


class RawProductBase(BaseModel):
    """Base model for raw product data from CSV"""

    product_key: str
    system_name: str
    friendly_name: str


class RawCategoryBase(BaseModel):
    """Base model for raw category data from CSV"""

    category_key: str
    system_name: str
    friendly_name: str


class RawAttributeBase(BaseModel):
    """Base model for raw attribute data from CSV"""

    attribute_key: str
    system_name: str
    friendly_name: str
    attribute_type: str
    unit_measure_type: str


class RawProductCategoryBase(BaseModel):
    """Base model for raw product-category relationship data from CSV"""

    product_key: str
    category_key: str


class RawCategoryAttributeBase(BaseModel):
    """Base model for raw category-attribute relationship data from CSV"""

    category_key: str
    attribute_key: str


class RawProductAttributeValueBase(BaseModel):
    """Base model for raw product attribute value data from CSV"""

    product_key: str
    attribute_key: str
    value: str


class RawProductAttributeGapBase(BaseModel):
    """Base model for raw product attribute gap data from CSV"""

    product_key: str
    attribute_key: str


class RawProductAttributeAllowableValueBase(BaseModel):
    """Base model for raw product attribute allowable value data from CSV"""

    product_key: str
    attribute_key: str
    value: str


class RawCategoryAllowableValueBase(BaseModel):
    """Base model for raw category allowable value data from CSV"""

    category_key: str
    attribute_key: str
    value: str
    unit_type: str | None = None
    minimum_value: float | None = None
    minimum_unit: str | None = None
    maximum_value: float | None = None
    maximum_unit: str | None = None
    range_qualifier: str | None = None


class RawRecommendationBase(BaseModel):
    """Base model for raw recommendation data from CSV"""

    recommendation_key: str
    product_key: str
    attribute_key: str
    value: str
    confidence: float


class RawRichTextSourceBase(BaseModel):
    """Base model for raw rich text source data from CSV"""

    source_key: str
    product_key: str
    content: str
    name: str
    priority: int
    created_at: datetime
