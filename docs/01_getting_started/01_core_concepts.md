# Core Concepts

## Facet Inference

Facet inference is the process of predicting appropriate labels for product attributes (facets) based on available product information. The system uses LLMs to analyse product data and make intelligent predictions about missing or ambiguous facet values.

### Key Components

1. **FacetDefinition**
   - Defines a facet (e.g., "gender", "material", "style")
   - Specifies acceptable labels
   - Configures rules for multiple labels and nullability

2. **ProductInfo**
   - Contains product details (name, description, category)
   - Includes additional attributes
   - Used as input for facet prediction

3. **FacetPrediction**
   - Contains predicted labels
   - Includes confidence scoring
   - May suggest new labels if needed
   - Provides reasoning for predictions

### Confidence Scoring

The system uses a numerical confidence score (0-1) with the following bands:

- **Certain (98-100%)**: The value is not just overwhelmingly likely, but it is logically or definitionally impossible for any other value to be correct. There is no sane, reasonable, or even pedantic way to argue for a different answer. This is a very rare case.
- **Very High (95-98%)**: The value is either explicitly stated or so overwhelmingly obvious from direct evidence, established rules, or common sense that only the most pedantic doubt could exist. This includes cases where the product's documentation, specifications, or images directly confirm the value, or where the treatment of similar products is so consistent that the answer is indisputable.
- **High (85-95%)**: The value is not directly stated, but can be confidently inferred from strong, consistent patterns in the data, context, or domain knowledge. Also includes cases where the answer is exceedingly obvious to any reasonable person, even if not directly stated. However, there is a small chance of error if an exception exists.
- **Moderate (60-85%)**: The value is an educated guess based on partial evidence, weak patterns, or indirect clues. There is some support for the answer, but also significant uncertainty or possible exceptions. Alternatively, the answer is plausible based on general knowledge, but there is no supporting evidence in the product info or comparable products.
- **Low (30-60%)**: The value is a weak guess with little supporting evidence. The inference is based on vague similarities, general assumptions, or incomplete information. There is a high likelihood of error.
- **Very Low (0-30%)**: The value is a pure guess or based on almost no evidence. There is no meaningful information to support the answer, and it is essentially a placeholder or random choice.

### Prediction States

A prediction can be in one of several states:
1. **Has Labels**: One or more labels were predicted
2. **Needs New Label**: Existing labels are insufficient
3. **Nullable**: No labels apply (when allowed)
4. **Insufficient Info**: Not enough information to make a prediction

## Usage Example
```python
from src.core.facet_inference.models import FacetDefinition, ProductInfo
from src.core.facet_inference.service import FacetInferenceService

# Define a facet
facet = FacetDefinition(
    name="gender",
    acceptable_labels=["men", "women", "unisex"],
    allow_multiple=False,
    is_nullable=False
)

# Create product info
product = ProductInfo(
    name="Classic Fit T-Shirt",
    description="A comfortable, relaxed fit t-shirt",
    category="Clothing",
    attributes={"material": "cotton"}
)

# Get predictions
service = FacetInferenceService()
prediction = await service.predict_facet(product, facet)
``` 
