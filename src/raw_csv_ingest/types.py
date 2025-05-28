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


class RawAttributeAllowableValueApplicableInEveryCategoryBase(BaseModel):
    """Base model for raw attribute allowable value applicable in every category data from CSV"""

    attribute_key: str
    value: str


class RawAttributeAllowableValueInAnyCategoryBase(BaseModel):
    """Base model for raw attribute allowable value in any category data from CSV"""

    attribute_key: str
    value: str


class RawRecommendationBase(BaseModel):
    """Base model for raw recommendation data from CSV"""

    recommendation_key: str
    product_key: str
    attribute_key: str
    value: str
    confidence: float
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class RawRecommendationRoundBase(BaseModel):
    """Base model for raw recommendation round data from CSV"""

    round_key: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class RawRichTextSourceBase(BaseModel):
    """Base model for raw rich text source data from CSV"""

    source_key: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())


# Create DTOs
class RawProductCreate(RawProductBase):
    """DTO for creating a new raw product"""
    pass


class RawCategoryCreate(RawCategoryBase):
    """DTO for creating a new raw category"""
    pass


class RawAttributeCreate(RawAttributeBase):
    """DTO for creating a new raw attribute"""
    pass


class RawProductCategoryCreate(RawProductCategoryBase):
    """DTO for creating a new raw product-category relationship"""
    pass


class RawCategoryAttributeCreate(RawCategoryAttributeBase):
    """DTO for creating a new raw category-attribute relationship"""
    pass


class RawProductAttributeValueCreate(RawProductAttributeValueBase):
    """DTO for creating a new raw product attribute value"""
    pass


class RawProductAttributeGapCreate(RawProductAttributeGapBase):
    """DTO for creating a new raw product attribute gap"""
    pass


class RawProductAttributeAllowableValueCreate(RawProductAttributeAllowableValueBase):
    """DTO for creating a new raw product attribute allowable value"""
    pass


class RawCategoryAllowableValueCreate(RawCategoryAllowableValueBase):
    """DTO for creating a new raw category allowable value"""
    pass


class RawAttributeAllowableValueApplicableInEveryCategoryCreate(RawAttributeAllowableValueApplicableInEveryCategoryBase):
    """DTO for creating a new raw attribute allowable value applicable in every category"""
    pass


class RawAttributeAllowableValueInAnyCategoryCreate(RawAttributeAllowableValueInAnyCategoryBase):
    """DTO for creating a new raw attribute allowable value in any category"""
    pass


class RawRecommendationCreate(RawRecommendationBase):
    """DTO for creating a new raw recommendation"""
    pass


class RawRecommendationRoundCreate(RawRecommendationRoundBase):
    """DTO for creating a new raw recommendation round"""
    pass


class RawRichTextSourceCreate(RawRichTextSourceBase):
    """DTO for creating a new raw rich text source"""
    pass 