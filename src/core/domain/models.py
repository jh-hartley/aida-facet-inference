from pydantic import BaseModel, Field

from src.core.domain.confidence_levels import ConfidenceLevel
from src.core.domain.types import (
    ProductAttributeGap,
    ProductAttributeValue,
    ProductDescriptor,
)


class ProductDetails(BaseModel):
    """
    Complete product information including all related data.

    This is provided to the LLM to use as context when generating facets.
    """

    product_key: str  # Database UUID
    product_code: str  # EAN/system_name
    code_type: str
    product_name: str
    product_description: list[ProductDescriptor]
    categories: list[str]
    attributes: list[ProductAttributeValue]

    def _normalise_value(self, value: str) -> str:
        normalised = " ".join(value.lower().split())

        for char in ".,;:!?":
            normalised = normalised.replace(char, "")

        for suffix in [
            " inc",
            " ltd",
            " limited",
            " llc",
            " corp",
            " corporation",
        ]:
            if normalised.endswith(suffix):
                normalised = normalised[: -len(suffix)]

        return normalised

    def get_formatted_description(self) -> str:
        processed_descriptions = []
        for desc in self.product_description:
            if not desc.value.strip():
                continue

            category = desc.descriptor.split("//")[0]
            normalised_value = self._normalise_value(desc.value)
            processed_descriptions.append((category, normalised_value))

        seen_values = set()
        grouped_descriptions: dict[str, list[str]] = {}

        for category, value in processed_descriptions:
            if value in seen_values:
                continue
            seen_values.add(value)

            if category not in grouped_descriptions:
                grouped_descriptions[category] = []
            grouped_descriptions[category].append(value)

        formatted_sections = []
        for category, values in grouped_descriptions.items():
            formatted_sections.append(f"{category}:")
            formatted_sections.extend(f"- {value}" for value in values)
            formatted_sections.append("")

        return "\n".join(formatted_sections)

    def get_formatted_attributes(self) -> str:
        """Get a formatted string of all product attributes."""
        formatted_attrs = []
        for attr in self.attributes:
            value = attr.value.replace("||", " ")
            formatted_attrs.append(f"{attr.attribute}: {value}")
        return "\n".join(formatted_attrs)

    def get_llm_prompt(self) -> str:
        """
        Get a formatted string of product information for LLM consumption.
        """
        sections = [
            f"Product Name: {self.product_name or '[Name not available]'}",
            f"Product Code ({self.code_type}): {self.product_code}",
            f"Product Key (UUID): {self.product_key}",
            "",
            "Product Description:\n",
            self.get_formatted_description(),
            "Categories:",
            *[f"- {cat}" for cat in self.categories],
            "",
            "Attributes:",
            self.get_formatted_attributes(),
            "",
        ]
        return "\n".join(sections)


class ProductGaps(BaseModel):
    """
    Information about missing attribute values for a product.

    This is provided to the LLM to use as context when generating
    recommendations for filling in missing attribute values.
    """

    product_code: str
    product_name: str
    gaps: list[ProductAttributeGap]

    def get_formatted_gaps(self) -> str:
        """Get a formatted string of all product gaps."""
        return "\n".join(
            f"{gap.attribute}:\n"
            f"  Allowed values: {', '.join(gap.allowable_values)}"
            for gap in self.gaps
        )

    def get_llm_prompt(self) -> str:
        """Get a formatted string of gap information for LLM consumption."""
        sections = [
            f"Product Code: {self.product_code}",
            f"Product Name: {self.product_name}",
            "",
            "Missing Attributes:",
            self.get_formatted_gaps(),
        ]
        return "\n".join(sections)


class FacetPrediction(BaseModel):
    """Domain model for a facet prediction result."""

    attribute: str = Field(description="Name of the attribute being predicted")
    recommendation: str = Field(
        description="The recommended value for the attribute",
        default="",
    )
    unit: str = Field(
        description="Unit of the attribute, empty string if non-numeric data",
        default="",
    )
    confidence: float = Field(
        description="Confidence score (0-1) for the prediction", ge=0.0, le=1.0
    )
    reasoning: str = Field(
        description="Explanation for why this value was chosen"
    )
    missing_value: str = Field(
        description="Missing value when the correct value is not in the allowed list and none of the allowed values are even a rough fit; otherwise empty string",
        default="",
    )

    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Get the confidence level for this prediction."""
        return ConfidenceLevel.from_score(self.confidence)
