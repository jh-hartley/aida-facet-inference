# Core Concepts

## Facet Inference

Facet inference is the process of predicting appropriate labels for product attributes (facets) based on available product information. The system uses LLMs to analyze product data and make intelligent predictions about missing or ambiguous facet values.

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

The system uses a numerical confidence score (0-1) with corresponding linguistic levels:
- VERY_HIGH (0.9-1.0): Extremely confident
- HIGH (0.7-0.89): Very confident
- MODERATE (0.5-0.69): Moderately confident
- LOW (0.3-0.49): Somewhat confident
- VERY_LOW (0.0-0.29): Not very confident

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