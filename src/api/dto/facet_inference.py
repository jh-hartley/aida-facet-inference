from pydantic import BaseModel

from src.core.facet_inference.models import FacetPrediction


class ProductDescriptorRequest(BaseModel):
    """Request model for a product descriptor."""

    descriptor: str
    value: str


class ProductAttributeValueRequest(BaseModel):
    """Request model for a product attribute value."""

    attribute: str
    value: str


class ProductAttributeGapRequest(BaseModel):
    """Request model for a product attribute gap."""

    attribute: str
    allowable_values: list[str]


class ProductDetailsRequest(BaseModel):
    """Request model for product details."""

    product_code: str
    product_name: str
    product_description: list[ProductDescriptorRequest]
    categories: list[str]
    attributes: list[ProductAttributeValueRequest]


class ProductGapsRequest(BaseModel):
    """Request model for product gaps."""

    product_code: str
    product_name: str
    gaps: list[ProductAttributeGapRequest]


class FacetPredictionResponse(BaseModel):
    """Response model for a single facet prediction."""

    prediction: FacetPrediction


class FacetPredictionsResponse(BaseModel):
    """Response model for multiple facet predictions."""

    predictions: list[FacetPrediction]
