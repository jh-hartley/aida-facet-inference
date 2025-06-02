from datetime import datetime

from pydantic import BaseModel


class RawProduct(BaseModel):
    """Base model for raw product data from CSV"""

    product_key: str
    system_name: str
    friendly_name: str


class RawCategory(BaseModel):
    """Base model for raw category data from CSV"""

    category_key: str
    system_name: str
    friendly_name: str


class RawAttribute(BaseModel):
    """Base model for raw attribute data from CSV"""

    attribute_key: str
    system_name: str
    friendly_name: str
    attribute_type: str
    unit_measure_type: str


class RawProductCategory(BaseModel):
    """Base model for raw product-category relationship data from CSV"""

    product_key: str
    category_key: str


class RawCategoryAttribute(BaseModel):
    """Base model for raw category-attribute relationship data from CSV"""

    category_key: str
    attribute_key: str


class RawProductAttributeValue(BaseModel):
    """Base model for raw product attribute value data from CSV"""

    product_key: str
    attribute_key: str
    value: str


class RawProductAttributeGap(BaseModel):
    """Base model for raw product attribute gap data from CSV"""

    product_key: str
    attribute_key: str


class RawProductAttributeAllowableValue(BaseModel):
    """Base model for raw product attribute allowable value data from CSV"""

    product_key: str
    attribute_key: str
    value: str


class RawCategoryAllowableValue(BaseModel):
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


class RawRecommendation(BaseModel):
    """Base model for raw recommendation data from CSV"""

    recommendation_key: str
    product_key: str
    attribute_key: str
    value: str
    confidence: float


class RawRichTextSource(BaseModel):
    """Base model for raw rich text source data from CSV"""

    source_key: str
    product_key: str
    content: str
    name: str
    priority: int
    created_at: datetime


class HumanRecommendation(BaseModel):
    product_reference: str
    attribute_reference: str
    attribute_name: str
    recommendation: str
    unit: str
    override: str
    alternative_override: str
    action: str
    link_to_site: str
    comment: str
