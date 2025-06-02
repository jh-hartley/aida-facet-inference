from datetime import datetime

from pydantic import BaseModel


class RawProduct(BaseModel):
    product_key: str
    system_name: str
    friendly_name: str


class RawCategory(BaseModel):
    category_key: str
    system_name: str
    friendly_name: str


class RawAttribute(BaseModel):
    attribute_key: str
    system_name: str
    friendly_name: str
    attribute_type: str
    unit_measure_type: str


class RawProductCategory(BaseModel):
    product_key: str
    category_key: str


class RawCategoryAttribute(BaseModel):
    category_key: str
    attribute_key: str


class RawProductAttributeValue(BaseModel):
    product_key: str
    attribute_key: str
    value: str


class RawProductAttributeGap(BaseModel):
    product_key: str
    attribute_key: str


class RawProductAttributeAllowableValue(BaseModel):
    product_key: str
    attribute_key: str
    value: str


class RawCategoryAllowableValue(BaseModel):
    category_key: str
    attribute_key: str
    value: str
    unit_type: str | None
    minimum_value: float | None
    minimum_unit: str | None
    maximum_value: float | None
    maximum_unit: str | None
    range_qualifier: str | None


class RawRecommendation(BaseModel):
    recommendation_key: str
    product_key: str
    attribute_key: str
    value: str
    confidence: float


class RawRichTextSource(BaseModel):
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
