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
    
    product_key: str  # Database UUID
    product_code: str  # EAN/system_name
    product_name: str
    product_description: list[ProductDescriptor]
    categories: list[str]
    attributes: list[ProductAttributeValue]
    code_type: str  # Type of product code (EAN, UPC, ISBN, etc.)

    def get_formatted_description(self) -> str:
        """Get a formatted string of all product descriptions."""
        return "\n".join(
            f"{desc.descriptor}: {desc.value}"
            for desc in self.product_description
        )

    def get_formatted_attributes(self) -> str:
        """Get a formatted string of all product attributes."""
        return "\n".join(
            f"{attr.attribute}: {attr.value}" for attr in self.attributes
        )

    def get_llm_prompt(self) -> str:
        """
        Get a formatted string of product information for LLM consumption.
        """
        sections = [
            f"Product Code ({self.code_type}): {self.product_code}",
            f"Product Key (UUID): {self.product_key}",
            f"Product Name: {self.product_name}",
            "",
            "Product Description:",
            self.get_formatted_description(),
            "",
            "Categories:",
            *[f"- {cat}" for cat in self.categories],
            "",
            "Attributes:",
            self.get_formatted_attributes(),
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
