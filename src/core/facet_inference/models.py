from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class ConfidenceBand:
    name: str
    label: str
    min_score: float
    max_score: float
    range_str: str
    description: str
    example: str


CONFIDENCE_BANDS: list[ConfidenceBand] = [
    ConfidenceBand(
        name="VERY_HIGH",
        label="Very High",
        min_score=0.9,
        max_score=1.0,
        range_str="90-100%",
        description="Direct evidence in product details.",
        example="The product description explicitly states the value.",
    ),
    ConfidenceBand(
        name="HIGH",
        label="High",
        min_score=0.7,
        max_score=0.89,
        range_str="70-89%",
        description="Strong indirect evidence.",
        example="Category and attributes strongly suggest the value.",
    ),
    ConfidenceBand(
        name="MODERATE",
        label="Moderate",
        min_score=0.5,
        max_score=0.69,
        range_str="50-69%",
        description="Clear inference from context.",
        example="Similar products or multiple clues point to the value.",
    ),
    ConfidenceBand(
        name="LOW",
        label="Low",
        min_score=0.3,
        max_score=0.49,
        range_str="30-49%",
        description="Weak inference or partial evidence.",
        example="Some hints, but not conclusive.",
    ),
    ConfidenceBand(
        name="VERY_LOW",
        label="Very Low",
        min_score=0.0,
        max_score=0.29,
        range_str="0-29%",
        description="Minimal evidence or ambiguous.",
        example="No relevant information; answer is a guess.",
    ),
]


class ConfidenceLevel(str, Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceLevel":
        for band in CONFIDENCE_BANDS:
            if band.min_score <= score <= band.max_score:
                return cls[band.name]
        return cls.VERY_LOW  # fallback

    @classmethod
    def get_prompt_description(cls) -> str:
        return "\n".join(
            f"{band.label} ({band.range_str}): {band.description} "
            f"Example: {band.example}"
            for band in CONFIDENCE_BANDS
        )

    @classmethod
    def get_band(cls, level: "ConfidenceLevel") -> ConfidenceBand:
        for band in CONFIDENCE_BANDS:
            if cls[band.name] == level:
                return band
        raise ValueError(f"No band found for level {level}")


class FacetPrediction(BaseModel):
    """Domain model for a facet prediction result."""

    attribute: str = Field(description="Name of the attribute being predicted")
    predicted_value: str = Field(
        description="The predicted value for the attribute"
    )
    confidence: float = Field(
        description="Confidence score (0-1) for the prediction", ge=0.0, le=1.0
    )
    reasoning: str = Field(
        description="Explanation for why this value was chosen"
    )
    suggested_value: str = Field(
        description="Suggested value when the correct value is not in the "
        "allowed list"
    )

    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Get the confidence level for this prediction."""
        return ConfidenceLevel.from_score(self.confidence)

    @classmethod
    def get_prompt_description(cls) -> str:
        """
        Get a formatted description of the response structure for prompts.
        """
        return """
        {
            "attribute": str,  # Name of the attribute being predicted
            "predicted_value": str,  # The predicted value (empty string if no
                # prediction possible)
            "confidence": float,  # Confidence score between 0 and 1
            "reasoning": str,  # Explanation for the prediction
            "suggested_value": str  # Suggested value if correct value not in
                # allowed list
        }
        """
