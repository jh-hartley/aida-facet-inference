from dataclasses import dataclass
from enum import Enum


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
        name="CERTAIN",
        label="Certain",
        min_score=0.98,
        max_score=1.0,
        range_str="98-100%",
        description=(
            "The value is not just overwhelmingly likely, but it is logically or definitionally impossible for any other value to be correct. "
            "There is no sane, reasonable, or even pedantic way to argue for a different answer."
        ),
        example=(
            "The product is described as 'This is a 3-step aluminum step ladder, model SL-3000.' The only possible value for 'number of steps' is 3, and for 'material' is aluminum."
        ),
    ),
    ConfidenceBand(
        name="VERY_HIGH",
        label="Very High",
        min_score=0.95,
        max_score=0.9799,
        range_str="95-98%",
        description=(
            "The value is either explicitly stated or so overwhelmingly obvious from direct evidence, established rules, or common sense that only the most pedantic doubt could exist. "
            "This includes cases where the product's documentation, specifications, or images directly confirm the value, or where the treatment of similar products is so consistent that the answer is indisputable."
        ),
        example=(
            "The product description says: 'This ladder features a patented locking mechanism.'\n"
            "All products in this category with a certain feature are always classified the same way, and this product matches exactly."
        ),
    ),
    ConfidenceBand(
        name="HIGH",
        label="High",
        min_score=0.85,
        max_score=0.9499,
        range_str="85-95%",
        description=(
            "The value is not directly stated, but can be confidently inferred from strong, consistent patterns in the data, context, or domain knowledge. "
            "Also includes cases where the answer is exceedingly obvious to any reasonable person, even if not directly stated. However, there is a small chance of error if an exception exists."
        ),
        example=(
            "The product is a refrigerator; it is obvious to anyone that it is an appliance, even if not stated.\n"
            "The product is in a category where all items are always classified as 'outdoor use,' and this product fits all the criteria, but the description doesn't say so directly."
        ),
    ),
    ConfidenceBand(
        name="MODERATE",
        label="Moderate",
        min_score=0.6,
        max_score=0.8499,
        range_str="60-85%",
        description=(
            "The value is an educated guess based on partial evidence, weak patterns, or indirect clues. There is some support for the answer, but also significant uncertainty or possible exceptions. "
            "Alternatively, the answer is plausible based on general knowledge, but there is no supporting evidence in the product info or comparable products."
        ),
        example=(
            "The product is a step ladder, and most step ladders don't mention a locking mechanism, so it's guessed that this one doesn't have one, but there are exceptions.\n"
            "A product is a kitchen gadget, and it is plausible it is used for food prep, but there is no direct or pattern-based evidence."
        ),
    ),
    ConfidenceBand(
        name="LOW",
        label="Low",
        min_score=0.3,
        max_score=0.5999,
        range_str="30-60%",
        description=(
            "The value is a weak guess with little supporting evidence. The inference is based on vague similarities, general assumptions, or incomplete information. There is a high likelihood of error."
        ),
        example=(
            "The product is a ladder, and some ladders have locking mechanisms, but there's no information about this specific type.\n"
            "The product is in a broad category with mixed treatment of the attribute in question."
        ),
    ),
    ConfidenceBand(
        name="VERY_LOW",
        label="Very Low",
        min_score=0.0,
        max_score=0.2999,
        range_str="0-30%",
        description=(
            "The value is a pure guess or based on almost no evidence. There is no meaningful information to support the answer, and it is essentially a placeholder or random choice."
        ),
        example=(
            "The product description and category provide no clues about the attribute.\n"
            "The attribute is rarely mentioned for this type of product, and there is no pattern to follow."
        ),
    ),
]


class ConfidenceLevel(str, Enum):
    CERTAIN = "certain"
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
