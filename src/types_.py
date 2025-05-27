from datetime import datetime

from pydantic import BaseModel, Field

from src.config import config


class RetailerBase(BaseModel):
    """Base model for Retailer data"""

    name: str
    url: str
    country: str
    industry: str


class ProductBase(BaseModel):
    """Base model for Product data"""

    identifier_value: str
    identifier_type: str
    name: str
    description: str
    category: str
    attributes: dict  # JSONB in DB


class ProductEmbeddingBase(BaseModel):
    """Base model for Product Embedding"""

    embedding_model: str
    embedding: list[float] = Field(
        min_length=config.EMBEDDING_MIN_DIMENSIONS,
        max_length=config.EMBEDDING_MAX_DIMENSIONS,
    )


class RetailerFacetBase(BaseModel):
    """Base model for Retailer Facet data"""

    name: str
    description: str


class RetailerProductBase(BaseModel):
    """Base model for Retailer Product data"""

    retailer_product_id: str
    url: str
    price: float
    availability: bool


class RetailerProductAttributeBase(BaseModel):
    """Base model for Retailer Product Attribute data"""

    attribute_name: str
    attribute_value: str
    attribute_type: str


class AttributeMappingBase(BaseModel):
    """Base model for Attribute Mapping data"""

    source_attribute: str
    normalised_attribute: str
    confidence: float


class RetailerCreate(RetailerBase):
    """DTO for creating a new retailer"""

    pass


class ProductCreate(ProductBase):
    """DTO for creating a new product"""

    pass


class ProductEmbeddingCreate(ProductEmbeddingBase):
    """DTO for creating a new product embedding"""

    product_id: int


class RetailerFacetCreate(RetailerFacetBase):
    """DTO for creating a new retailer facet"""

    retailer_id: int


class RetailerProductCreate(RetailerProductBase):
    """DTO for creating a new retailer product"""

    retailer_id: int
    product_id: int


class RetailerProductAttributeCreate(RetailerProductAttributeBase):
    """DTO for creating a new retailer product attribute"""

    retailer_id: int
    retailer_product_id: int


class AttributeMappingCreate(AttributeMappingBase):
    """DTO for creating a new attribute mapping"""

    retailer_id: int


# Update DTOs
class RetailerUpdate(RetailerBase):
    """DTO for updating a retailer"""

    name: str
    url: str


class ProductUpdate(ProductBase):
    """DTO for updating a product"""

    identifier_value: str
    identifier_type: str
    name: str


class RetailerProductUpdate(RetailerProductBase):
    """DTO for updating a retailer product"""

    retailer_product_id: str
    url: str
    price: float
    availability: bool


class RetailerView(RetailerBase):
    """DTO for retailer view"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductView(ProductBase):
    """DTO for product view"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductEmbeddingView(ProductEmbeddingBase):
    """DTO for product embedding view"""

    id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RetailerFacetView(RetailerFacetBase):
    """DTO for retailer facet view"""

    id: int
    retailer_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RetailerProductView(RetailerProductBase):
    """DTO for retailer product view"""

    id: int
    retailer_id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RetailerProductAttributeView(RetailerProductAttributeBase):
    """DTO for retailer product attribute view"""

    retailer_id: int
    retailer_product_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AttributeMappingView(AttributeMappingBase):
    """DTO for attribute mapping view"""

    id: int
    retailer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
