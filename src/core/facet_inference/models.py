from enum import Enum

from pydantic import BaseModel, Field


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
            "predicted_value": str,  # The predicted value
            "confidence": float,  # Confidence score between 0 and 1
            "reasoning": str  # Explanation for the prediction
        }
        """
