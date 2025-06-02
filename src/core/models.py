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
    code_type: str
    product_name: str
    product_description: list[ProductDescriptor]
    categories: list[str]
    attributes: list[ProductAttributeValue]

    def get_formatted_description(self) -> str:
        """Get a formatted string of all product descriptions."""
        grouped_descriptions: dict[str, list[str]] = {}

        for desc in self.product_description:
            if not desc.value.strip():
                continue

            category = desc.descriptor.split("//")[0]

            if desc.value in grouped_descriptions.get(category, []):
                continue

            if category not in grouped_descriptions:
                grouped_descriptions[category] = []
            grouped_descriptions[category].append(desc.value)

        formatted_sections = []
        for category, values in grouped_descriptions.items():
            formatted_sections.append(f"{category}:")
            formatted_sections.extend(f"- {value}" for value in values)
            formatted_sections.append(
                ""
            )  # Consistent spacing after each section

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
