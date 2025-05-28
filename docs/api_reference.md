# API Reference

## Facet Inference Service

### `FacetInferenceService`

The main service class for facet inference operations.

```python
from src.core.facet_inference.service import FacetInferenceService

service = FacetInferenceService(predictor=None)  # predictor is optional
```

#### Methods

##### `predict_facet`

```python
async def predict_facet(
    self,
    product: ProductInfo,
    facet: FacetDefinition,
) -> FacetPrediction
```

Predicts labels for a single product facet.

**Parameters:**
- `product`: Product information to analyze
- `facet`: Facet definition with acceptable labels

**Returns:**
- `FacetPrediction` containing the prediction results

##### `predict_multiple_facets`

```python
async def predict_multiple_facets(
    self,
    product: ProductInfo,
    facets: Sequence[FacetDefinition],
) -> list[FacetPrediction]
```

Predicts labels for multiple product facets concurrently.

**Parameters:**
- `product`: Product information to analyze
- `facets`: List of facet definitions to predict

**Returns:**
- List of `FacetPrediction` results

## Models

### `ProductInfo`

```python
class ProductInfo(BaseModel):
    ean: str
    name: str
    description: str
    category: str
    attributes: dict[str, str]
```

### `FacetDefinition`

```python
class FacetDefinition(BaseModel):
    name: str
    acceptable_labels: list[str]
    allow_multiple: bool = False
    is_nullable: bool = False
```

### `FacetPrediction`

```python
class FacetPrediction(BaseModel):
    facet_name: str
    labels: list[str]
    confidence: float
    reasoning: str
    suggested_label: str | None = None
```

#### Properties

- `confidence_level`: Returns the linguistic confidence level
- `has_sufficient_info`: Whether enough information was available
- `needs_new_label`: Whether a new label was suggested
- `is_nullable`: Whether no labels apply (when allowed)

## LLM Integration

### `ProductFacetPredictor`

```python
from src.core.facet_inference.inference import ProductFacetPredictor
from src.core.llm.models import LlmModel

predictor = ProductFacetPredictor(llm_model=LlmModel.GPT_4O_MINI)
```

#### Methods

##### `predict`

```python
async def predict(
    self,
    product: ProductInfo,
    facet: FacetDefinition,
) -> FacetPrediction
```

Makes a prediction using the LLM.

**Parameters:**
- `product`: Product information to analyze
- `facet`: Facet definition with acceptable labels

**Returns:**
- `FacetPrediction` containing the prediction results 