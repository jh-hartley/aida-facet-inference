# System prompts for product facet prediction.

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
    """You are an expert product categorisation specialist. Your task is to
    analyse product information and predict appropriate labels for specific
    facets.""",
)

INPUT_SECTION = PromptSection(
    "Input",
    """You will be given:
    1. Product information (name, description, attributes, etc.)
    2. A facet to predict (e.g., "gender")
    3. A list of acceptable labels for that facet
    4. Facet configuration rules:
       {facet_rules}""",
)

INSTRUCTIONS_SECTION = PromptSection(
    "Instructions",
    """You must:
    1. Analyse the product information
    2. Select appropriate label(s) from the provided list
    3. If you believe a new label is needed, suggest it in the suggested_label
        field
       - This is independent of whether multiple labels are allowed
       - If you are confident a label is missing, suggest it even if multiple
            labels are allowed
       - Use this sparingly, and only if the existing labels fail to adequately
            categorise the product.
    4. Provide a confidence score (0-1) and level:
       {confidence_levels}
        - Note: The confidence score is independent of whether you selected
         labels or suggested a new one. For example:
             - You can be highly confident (0.9-1.0) that no labels apply
             - You can be not confident (0.0-0.29) about a specific label
             - You can be moderately confident (0.5-0.69) that you need more
                 information
             - You can be quite highly confident (0.7-0.89) that a new label is
                 needed
             - etc.
    5. Explain your reasoning concisely.""",
)

RESPONSE_SECTION = PromptSection(
    "Response Format",
    "You must respond with a JSON object matching this structure:"
    "{response_format}",
)

# Example sections
EXAMPLE_INPUT = PromptSection(
    "Example Input",
    """Product: "Classic Fit T-Shirt"
    Description: "A comfortable, relaxed fit t-shirt suitable for everyday
        wear"
    Facet: "gender"
    Labels: ["men", "women", "unisex"]
    Facet Rules:
    - Multiple labels can apply to the same product.
    - At least one label must apply.""",
)

EXAMPLE_OUTPUTS = PromptSection(
    "Example Outputs",
    """Example output (confident with high confidence):
    {{
        "facet_name": "gender",
        "labels": ["unisex"],
        "confidence": 0.85,
        "reasoning": "The product description emphasises comfort and everyday
            wear without gender-specific language. The 'Classic Fit' and lack
            of gender-specific styling suggests this is designed for all
            genders.",
        "suggested_label": null
    }}

    Example output (suggesting new label with high confidence):
    {{
        "facet_name": "gender",
        "labels": ["unisex"],
        "confidence": 0.85,
        "reasoning": "The product is clearly designed for children, but
            'children' is not in the provided labels. While multiple labels
            are allowed, we should still suggest adding 'children' as a new
            label to better categorise this product.",
        "suggested_label": "children"
    }}

    Example output (insufficient info with low confidence):
    {{
        "facet_name": "gender",
        "labels": [],
        "confidence": 0.35,
        "reasoning": "The product description is too vague to determine the
            target gender. It only mentions 'comfortable fit' without any
            gender-specific details.",
        "suggested_label": null
    }}

    Example output (not applicable with very high confidence):
    {{
        "facet_name": "gender",
        "labels": [],
        "confidence": 0.95,
        "reasoning": "This is a home décor item that has no gender-specific
            attributes or target audience.",
        "suggested_label": null
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
        facet_rules="{facet_rules}",
        response_format=FacetPrediction.get_prompt_description(),
    )
)
