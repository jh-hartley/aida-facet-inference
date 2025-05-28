from enum import Enum

from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    """Domain model for product information used in facet inference."""

    ean: str = Field(description="Product European Article Number (EAN)")
    name: str = Field(description="Product name")
    description: str = Field(description="Product description")
    category: str = Field(description="Product category")
    attributes: dict[str, str] = Field(
        description="Additional product attributes"
    )


class FacetDefinition(BaseModel):
    """Domain model for a facet definition."""

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

    def get_prompt_description(self) -> str:
        """
        Get a formatted description of the facet configuration for prompts.
        """
        rules = []
        if self.allow_multiple:
            rules.append("Multiple labels can apply to the same product.")
        else:
            rules.append("At most one label can apply.")
        if self.is_nullable:
            rules.append("No labels may apply.")
        else:
            rules.append("At least one label must apply.")
        return "\n".join(f"- {rule}" for rule in rules)


class ConfidenceLevel(str, Enum):
    """Linguistic descriptions of confidence levels."""

    VERY_HIGH = "very_high"  # 90-100%: Extremely confident
    HIGH = "high"  # 70-89%: Very confident
    MODERATE = "moderate"  # 50-69%: Moderately confident
    LOW = "low"  # 30-49%: Somewhat confident
    VERY_LOW = "very_low"  # 0-29%: Not very confident

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceLevel":
        """Convert a numerical score to a confidence level."""
        if score >= 0.9:
            return cls.VERY_HIGH
        elif score >= 0.7:
            return cls.HIGH
        elif score >= 0.5:
            return cls.MODERATE
        elif score >= 0.3:
            return cls.LOW
        else:
            return cls.VERY_LOW

    @classmethod
    def get_prompt_description(cls) -> str:
        """Get a formatted description of confidence levels for prompts."""
        return "\n".join(
            f"- {level.name} "
            f"({level.get_score_range()}): "
            f"{level.get_description()}"
            for level in cls
        )

    def get_score_range(self) -> str:
        """Get the score range for this confidence level."""
        ranges = {
            self.VERY_HIGH: "90-100%",
            self.HIGH: "70-89%",
            self.MODERATE: "50-69%",
            self.LOW: "30-49%",
            self.VERY_LOW: "0-29%",
        }
        return ranges[self]

    def get_description(self) -> str:
        """Get the linguistic description for this confidence level."""
        descriptions = {
            self.VERY_HIGH: "Extremely confident",
            self.HIGH: "Very confident",
            self.MODERATE: "Moderately confident",
            self.LOW: "Somewhat confident",
            self.VERY_LOW: "Not very confident",
        }
        return descriptions[self]


class FacetPrediction(BaseModel):
    """Domain model for a facet prediction result."""

    facet_name: str = Field(description="Name of the predicted facet")
    labels: list[str] = Field(
        description=(
            "List of predicted labels for the facet. Empty list "
            "indicates no labels apply or insufficient information."
        )
    )
    confidence: float = Field(
        description="Confidence score (0-1) for the prediction", ge=0.0, le=1.0
    )
    reasoning: str = Field(
        description="Explanation for why these labels were chosen"
    )
    suggested_label: str | None = Field(
        description=(
            "Optional suggested new label if existing labels are "
            "insufficient"
        ),
        default=None,
    )

    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Get the confidence level for this prediction."""
        return ConfidenceLevel.from_score(self.confidence)

    @property
    def has_sufficient_info(self) -> bool:
        """
        Whether the product information was sufficient to make a prediction.
        """
        return bool(self.labels) or self.suggested_label is not None

    @property
    def needs_new_label(self) -> bool:
        """Whether the LLM suggests adding a new label to the facet."""
        return self.suggested_label is not None

    @property
    def is_nullable(self) -> bool:
        """Whether the prediction indicates no labels should apply."""
        return (
            not self.labels
            and not self.suggested_label
            and self.has_sufficient_info
        )

    @classmethod
    def get_prompt_description(cls) -> str:
        """
        Get a formatted description of the response structure for prompts.
        """
        return """
        {{
            "facet_name": str,  # Name of the facet being predicted
            "labels": list[str],  # Selected labels (empty if none apply)
            "confidence": float,  # Confidence score between 0 and 1
            "reasoning": str,  # Explanation for the prediction
            "suggested_label": str  # New labels (empty if none apply)
        }}
        """
