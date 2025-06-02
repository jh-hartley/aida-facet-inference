from dataclasses import dataclass

from src.core.facet_inference.models import ConfidenceLevel, FacetPrediction


@dataclass
class PromptSection:
    """A section of a prompt with a title and content."""

    title: str
    content: str

    def format(self, **kwargs: str) -> str:
        """Format the section content with the given kwargs."""
        return self.content.format(**kwargs)

    def __str__(self) -> str:
        return f"{self.title}:\n{self.content}"


class PromptBuilder:
    """Builder for constructing structured prompts."""

    def __init__(self) -> None:
        self.sections: list[PromptSection] = []

    def add_section(self, title: str, content: str) -> "PromptBuilder":
        """Add a section to the prompt."""
        self.sections.append(PromptSection(title, content))
        return self

    def build(self, **kwargs: str) -> str:
        """Build the complete prompt with the given kwargs."""
        return "\n\n".join(
            section.format(**kwargs) for section in self.sections
        )


ROLE_SECTION = PromptSection(
    "Role",
    """You are an expert product attribute specialist. Your task is to
    analyse product information and predict appropriate values for missing
    attributes based on the product's details and the allowed values for
    each attribute.""",
)

INPUT_SECTION = PromptSection(
    "Input",
    """You will be given:
    1. Complete product information (name, description, categories, attributes)
    2. Information about a missing attribute and its allowed values
    3. Confidence level guidelines:
       {confidence_levels}""",
)

INSTRUCTIONS_SECTION = PromptSection(
    "Instructions",
    """You must:
    1. Analyse the product information carefully
    2. Select the most appropriate value from the allowed values list
    3. Provide a confidence score (0-1) and level:
       {confidence_levels}
        - Note: The confidence score reflects how certain you are about the
          prediction. For example:
             - You can be highly confident (0.9-1.0) about a clear match
             - You can be not confident (0.0-0.29) if the information is vague
             - You can be moderately confident (0.5-0.69) if there are some
               indicators but not definitive
             - etc.
    4. Explain your reasoning concisely.""",
)

RESPONSE_SECTION = PromptSection(
    "Response Format",
    "You must respond with a JSON object matching this structure:"
    "{response_format}",
)

# Example sections
EXAMPLE_INPUT = PromptSection(
    "Example Input",
    """Product Information:
    Product Code: ABC123
    Product Name: Classic Fit T-Shirt
    Product Description:
    Style: A comfortable, relaxed fit t-shirt suitable for everyday wear
    Material: 100% cotton
    Categories:
    - Clothing
    - T-Shirts
    - Men's Clothing
    Attributes:
    Brand: Generic
    Size: M
    Color: Blue

    Missing Attribute:
    Product Code: ABC123
    Product Name: Classic Fit T-Shirt
    Missing Attributes:
    Gender:
      Allowed values: Men, Women, Unisex""",
)

EXAMPLE_OUTPUTS = PromptSection(
    "Example Outputs",
    """Example output (confident with high confidence):
    {{
        "attribute": "Gender",
        "predicted_value": "Men",
        "confidence": 0.85,
        "reasoning": "The product is in the Men's Clothing category and the
            description emphasizes a classic fit, which strongly suggests this
            is designed for men."
    }}

    Example output (moderate confidence):
    {{
        "attribute": "Gender",
        "predicted_value": "Unisex",
        "confidence": 0.65,
        "reasoning": "While the product is in Men's Clothing, the description
            emphasizes comfort and everyday wear without gender-specific
            language, suggesting it could be suitable for all genders."
    }}

    Example output (low confidence):
    {{
        "attribute": "Gender",
        "predicted_value": "Unisex",
        "confidence": 0.35,
        "reasoning": "The product description is too vague to determine the
            target gender. It only mentions 'comfortable fit' without any
            gender-specific details."
    }}""",
)

PRODUCT_FACET_PREDICTION_PROMPT = (
    PromptBuilder()
    .add_section("Role", ROLE_SECTION.content)
    .add_section("Input", INPUT_SECTION.content)
    .add_section("Instructions", INSTRUCTIONS_SECTION.content)
    .add_section("Response Format", RESPONSE_SECTION.content)
    .add_section("Example Input", EXAMPLE_INPUT.content)
    .add_section("Example Outputs", EXAMPLE_OUTPUTS.content)
    .build(
        confidence_levels=ConfidenceLevel.get_prompt_description(),
        response_format=FacetPrediction.get_prompt_description(),
    )
)
