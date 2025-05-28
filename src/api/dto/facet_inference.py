import re

from pydantic import BaseModel, Field, field_validator

from src.core.facet_inference.models import FacetPrediction


class ProductInfoRequest(BaseModel):
    """Request model for product information."""

    ean: str = Field(description="Product European Article Number (EAN)")
    name: str = Field(description="Product name")
    description: str = Field(description="Product description")
    category: str = Field(description="Product category")
    attributes: dict[str, str] = Field(
        description="Additional product attributes", default_factory=dict
    )

    @field_validator("ean")
    @classmethod
    def validate_ean(cls, v: str) -> str:
        """Validate EAN format."""
        if not re.match(r"^\d{13}$", v):
            raise ValueError("EAN must be 13 digits")
        return v


class FacetDefinitionRequest(BaseModel):
    """Request model for facet definition."""

    name: str = Field(description="Name of the facet (e.g., 'gender')")
    acceptable_labels: list[str] = Field(
        description="List of valid labels for this facet"
    )
    allow_multiple: bool = Field(
        description="Whether multiple labels can apply simultaneously",
        default=False,
    )
    is_nullable: bool = Field(
        description="Whether no labels can apply (i.e., facet is optional)",
        default=False,
    )

    @field_validator("acceptable_labels")
    @classmethod
    def validate_labels(cls, v: list[str]) -> list[str]:
        """Validate acceptable labels."""
        if not v:
            raise ValueError("Must provide at least one acceptable label")
        return v


class FacetPredictionResponse(BaseModel):
    """Response model for a single facet prediction."""

    prediction: FacetPrediction


class FacetPredictionsResponse(BaseModel):
    """Response model for multiple facet predictions."""

    predictions: list[FacetPrediction]
