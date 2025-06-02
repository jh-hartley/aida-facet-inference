from dataclasses import dataclass
from typing import Protocol

from src.core.facet_inference.models import FacetPrediction
from src.core.models import ProductDetails
from src.core.types import ProductAttributeValue, ProductDescriptor


class ExampleProvider(Protocol):
    """Protocol for providing example product details and predictions."""

    def get_example_product(self) -> ProductDetails:
        """Get an example product for demonstration."""
        ...

    def get_example_predictions(self) -> list[FacetPrediction]:
        """Get example predictions for demonstration."""
        ...


class HardcodedExampleProvider:
    """A hardcoded example provider for demonstration purposes."""

    def get_example_product(self) -> ProductDetails:
        return ProductDetails(
            product_key="dummy-uuid-001",
            product_code="5397007196542",
            code_type="EAN",
            product_name="Classic Pine Louvre Door",
            product_description=[
                ProductDescriptor(
                    descriptor="General",
                    value=(
                        "A classic pine louvre door, ready to paint, "
                        "stain or varnish. Reversible opening, suitable for "
                        "internal use."
                    ),
                ),
                ProductDescriptor(
                    descriptor="Technical",
                    value=(
                        "This door features a traditional louvre design with "
                        "horizontal slats for ventilation. The pine "
                        "construction provides a natural, warm appearance."
                    ),
                ),
                ProductDescriptor(
                    descriptor="Usage",
                    value=(
                        "Ideal for wardrobes, pantries, and utility rooms "
                        "where ventilation is required."
                    ),
                ),
            ],
            categories=["Interior Doors", "Ventilation Doors"],
            attributes=[
                ProductAttributeValue(
                    attribute="Product height", value="762 mm"
                ),
                ProductAttributeValue(
                    attribute="Product thickness", value="21 mm"
                ),
                ProductAttributeValue(
                    attribute="Product width", value="610 mm"
                ),
                ProductAttributeValue(
                    attribute="Instructions for care",
                    value="Ready to paint, stain or varnish",
                ),
                ProductAttributeValue(
                    attribute="Surface preparation",
                    value="Ready to paint, stain or varnish",
                ),
                ProductAttributeValue(attribute="Location", value="Internal"),
                ProductAttributeValue(
                    attribute="Colour group", value="Neutral"
                ),
                ProductAttributeValue(attribute="Material", value="Pine"),
                ProductAttributeValue(attribute="Door style", value="Louvre"),
                ProductAttributeValue(
                    attribute="Product weight", value="4.7 kg"
                ),
                ProductAttributeValue(
                    attribute="Door opening direction", value="Reversible"
                ),
                ProductAttributeValue(attribute="Door type", value="Louvre"),
                ProductAttributeValue(attribute="Product type", value="Door"),
                ProductAttributeValue(attribute="Pack quantity", value="1"),
                ProductAttributeValue(attribute="Pack type", value="Each"),
            ],
        )

    def get_example_predictions(self) -> list[FacetPrediction]:
        # For clarity, we will show allowed_values for each example in the
        # markdown section above the JSON.
        # The FacetPrediction model itself does not have allowed_values, but
        # we will show them in the prompt output.
        return [
            # Example 1: VERY_HIGH - Direct evidence
            # Allowed values: ["Internal", "External"]
            FacetPrediction(
                attribute="Location",
                predicted_value="Internal",
                confidence=0.95,
                suggested_value="",
                reasoning=(
                    "The product description explicitly states "
                    "'suitable for internal use' and it's categorized as an "
                    "interior door."
                ),
            ),
            # Example 2: HIGH - Strong indirect evidence
            # Allowed values: ["Pine", "Oak", "MDF"]
            FacetPrediction(
                attribute="Material",
                predicted_value="Pine",
                confidence=0.85,
                suggested_value="",
                reasoning=(
                    "The product name includes 'Pine', the description "
                    "mentions 'pine construction', and it's listed in the "
                    "attributes. Multiple pieces of evidence strongly "
                    "indicate this is a pine door."
                ),
            ),
            # Example 3: MODERATE - Clear inference
            # Allowed values: ["Hollow", "Solid", "Panelled"]
            FacetPrediction(
                attribute="Construction type",
                predicted_value="Hollow",
                confidence=0.65,
                suggested_value="",
                reasoning=(
                    "While not explicitly stated, louvre doors of this type "
                    "are typically hollow construction to reduce weight while "
                    "maintaining strength. This is a common industry standard "
                    "for interior louvre doors."
                ),
            ),
            # Example 4: LOW - Weak inference (low-confidence guess, real
            # value)
            # Allowed values: ["White", "Natural", "Grey"]
            FacetPrediction(
                attribute="Colour group",
                predicted_value="White",
                confidence=0.20,
                suggested_value="",
                reasoning=(
                    "There is no mention of colour in the product details. "
                    "'White' is a common finish for interior doors, but this "
                    "is a guess."
                ),
            ),
            # Example 5: LOW - Weak inference (low-confidence guess, 'None'
            # value)
            # Allowed values: ["Clear", "Frosted", "None"]
            FacetPrediction(
                attribute="Glazed panel style",
                predicted_value="None",
                confidence=0.15,
                suggested_value="",
                reasoning=(
                    "There is no mention of glazing in the product details, "
                    "but 'None' is a plausible default for a louvre door."
                ),
            ),
            # Example 6: VERY_LOW - Minimal evidence
            # Allowed values: ["Standard", "Custom"]
            FacetPrediction(
                attribute="Installation type",
                predicted_value="Standard",
                confidence=0.10,
                suggested_value="",
                reasoning=(
                    "There's no specific information about installation. This "
                    "is a guess based on it being a standard interior door, "
                    "but could be incorrect."
                ),
            ),
            # Example 7: Cannot make prediction (confidently assert no label
            # applies)
            # Allowed values: ["FD30", "FD60"]
            FacetPrediction(
                attribute="Fire rating",
                predicted_value="",
                confidence=0.95,
                suggested_value="",
                reasoning=(
                    "The product is clearly not fire-rated and none of the "
                    "allowed values are appropriate for this type of door."
                ),
            ),
            # Example 8: Value not in allowed list
            # Allowed values: ["Panelled", "Flush", "Moulded"]
            FacetPrediction(
                attribute="Door style",
                predicted_value="",
                confidence=0.95,
                suggested_value="Louvre",
                reasoning=(
                    "The product is clearly a louvre door (name, description, "
                    "and attributes all confirm this), but 'Louvre' is not in "
                    "the allowed values list. This appears to be an error in "
                    "the allowed values."
                ),
            ),
        ]

    def _get_input_section(self) -> str:
        return """# Input
You will be given:
1. Complete product information (name, description, categories, attributes)
2. Information about a missing attribute and its allowed values
3. Confidence level guidelines:
Very High (90-100%): Direct evidence in product details. Example: The product
    description explicitly states the value.
High (70-89%): Strong indirect evidence. Example: Multiple attributes or
    descriptions strongly suggest the value.
Moderate (50-69%): Clear inference from context. Example: Common industry
    standards or typical usage patterns suggest the value.
Low (30-49%): Weak inference or partial evidence. Example: Some hints, but not
    conclusive.
Very Low (0-29%): Minimal evidence or ambiguous. Example: No relevant
    information; answer is a guess.

Note: You may use the product's EAN code to look up additional information
    if available. If you do so, explain this in your
    reasoning."""

    def _get_instructions_section(self) -> str:
        return """# Instructions
You must:
1. Analyze the product information carefully
2. Select the most appropriate value(s) from the allowed values list
3. Provide a confidence score (0-1) based on the guidelines
4. Explain your reasoning concisely
5. If you cannot find clear evidence for any value, select the most plausible
    value from the allowed list and assign a low confidence (e.g., 0.1–0.3),
    explaining your reasoning.
6. Only set predicted_value to an empty string if you are confident that none
    of the allowed values apply to the product. In this case, set confidence
    to high (e.g., 0.9) and explain why none of the values fit.
7. If the correct value is not in the allowed values list:
   - Set predicted_value to empty string
   - Set suggested_value to the correct value
   - Set confidence to high (0.7-0.9)
   - Explain why the value is missing from the allowed list
8. Special case for "None" values:
   - If you determine that "None" is the correct answer (e.g., no glazing present),
     but "None" is not in the allowed values list, treat this as case #7 above
   - Do not express confusion about "None" not being in the allowed values
   - Simply state that "None" is the correct value and explain why"""


@dataclass
class PromptTemplate:
    """A template for constructing prompts with placeholders."""

    template: str

    def format(self, **kwargs: str) -> str:
        """Format the template with the given kwargs."""
        return self.template.format(**kwargs)


class ProductFacetPrompt:
    """A simplified prompt system for product facet prediction."""

    def __init__(
        self, example_provider: ExampleProvider | None = None
    ) -> None:
        self.example_provider = example_provider or HardcodedExampleProvider()

    def get_system_prompt(self, product_context: str) -> str:
        """Get the complete system prompt."""
        sections = [
            self._get_role_section(),
            self._get_input_section(),
            self._get_instructions_section(),
            self._get_response_format_section(),
        ]

        if self.example_provider:
            sections.append("## Examples")
            sections.append(self._get_example_section())
            sections.append(self._get_example_outputs_section())

        sections.append(
            "\nNow, given the following product, perform the same prediction "
            "task:"
        )
        sections.append(self._get_product_context_section(product_context))

        return "\n\n".join(sections)

    def get_human_prompt(
        self, attribute: str, allowed_values: list[str]
    ) -> str:
        """Get the human prompt for a specific attribute prediction."""
        return f"""# Prediction Task
Predict a value for the following attribute:

**Attribute:** {attribute}
**Allowed values:** {', '.join(allowed_values)}"""

    def _get_role_section(self) -> str:
        return """# Role
You are an expert product attribute specialist. Your task is to analyze
product information and predict appropriate values for missing attributes
based on the product's details and the allowed values for each attribute."""

    def _get_input_section(self) -> str:
        return """# Input
You will be given:
1. Complete product information (name, description, categories, attributes)
2. Information about a missing attribute and its allowed values
3. Confidence level guidelines:
Very High (90-100%): Direct evidence in product details. Example: The product
    description explicitly states the value.
High (70-89%): Strong indirect evidence. Example: Multiple attributes or
    descriptions strongly suggest the value.
Moderate (50-69%): Clear inference from context. Example: Common industry
    standards or typical usage patterns suggest the value.
Low (30-49%): Weak inference or partial evidence. Example: Some hints, but not
    conclusive.
Very Low (0-29%): Minimal evidence or ambiguous. Example: No relevant
    information; answer is a guess.

Note: You may use the product's EAN code to look up additional information "
    "if available. If you do so, explain this in your reasoning."""

    def _get_instructions_section(self) -> str:
        return """# Instructions
You must:
1. Analyze the product information carefully
2. Select the most appropriate value(s) from the allowed values list
3. Provide a confidence score (0-1) based on the guidelines
4. Explain your reasoning concisely
5. If you cannot find clear evidence for any value, select the most plausible
    value from the allowed list and assign a low confidence (e.g., 0.1–0.3),
    explaining your reasoning.
6. Only set predicted_value to an empty string if you are confident that none
    of the allowed values apply to the product. In this case, set confidence
    to high (e.g., 0.9) and explain why none of the values fit.
7. If the correct value is not in the allowed values list:
   - Set predicted_value to empty string
   - Set suggested_value to the correct value
   - Set confidence to high (0.7-0.9)
   - Explain why the value is missing from the allowed list
8. Special case for "None" values:
   - If you determine that "None" is the correct answer (e.g., no glazing present),
     but "None" is not in the allowed values list, treat this as case #7 above
   - Do not express confusion about "None" not being in the allowed values
   - Simply state that "None" is the correct value and explain why"""

    def _get_response_format_section(self) -> str:
        return f"""# Response Format
You must respond with a JSON object matching this structure:
```json
{FacetPrediction.get_prompt_description()}
```"""

    def _get_example_section(self) -> str:
        if not self.example_provider:
            return ""

        example_product = self.example_provider.get_example_product()
        if hasattr(example_product, "get_llm_prompt"):
            return f"""## Example Input
{example_product.get_llm_prompt()}"""
        else:
            return ""

    def _get_example_outputs_section(self) -> str:
        # For each example, show allowed values above the JSON output
        examples = self.example_provider.get_example_predictions()
        allowed_values_map = [
            ["Internal", "External"],
            ["Pine", "Oak", "MDF"],
            ["Hollow", "Solid", "Panelled"],
            ["White", "Natural", "Grey"],
            ["Clear", "Frosted", "None"],
            ["Standard", "Custom"],
            ["FD30", "FD60"],
            ["Panelled", "Flush", "Moulded"],
        ]
        return "## Example Outputs\n" + "\n\n".join(
            f"### Example {i+1}\nAllowed values: {allowed_values_map[i]}\n"
            f"```json\n{prediction.model_dump_json(indent=2)}\n```"
            for i, prediction in enumerate(examples)
        )

    def _get_product_context_section(self, product_context: str) -> str:
        return f"""# Target Product
{product_context}"""


PRODUCT_FACET_PROMPT = ProductFacetPrompt()
