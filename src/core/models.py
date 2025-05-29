from pydantic import BaseModel

from src.core.types import (
    ProductAttributeGap,
    ProductAttributeValue,
    ProductDescriptor,
)


class ProductDetails(BaseModel):
    """
    Complete product information including all related data.

    This is provided to the LLM to use as context when generating facets.
    """

    product_code: str
    product_name: str
    product_description: list[ProductDescriptor]
    categories: list[str]
    attributes: list[ProductAttributeValue]


class ProductGaps(BaseModel):
    """
    Information about missing attribute values for a product.

    This is provided to the LLM to use as context when generating
    recommendations for filling in missing attribute values.
    """

    product_code: str
    product_name: str
    gaps: list[ProductAttributeGap]
