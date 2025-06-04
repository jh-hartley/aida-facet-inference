# API Reference

## HTTP API Endpoints

### Facet Inference Endpoints

#### `POST /facet-inference/predict/{product_key}`

Predicts values for all missing attributes of a product, identified by its unique product key.

- **Path Parameter:**
  - `product_key` (string, required): The unique identifier for the product (UUID or system key).

- **Request Body:**
  - _None required._ The product is identified by the path parameter.

- **Response:**
  Returns a JSON object with a list of predictions for all missing attributes of the product.

```json
{
  "predictions": [
    {
      "attribute": "gender",
      "recommendation": "mens",
      "unit": "",
      "confidence": 0.95,
      "reasoning": "Product description indicates this is a men's item",
      "suggested_value": null
    },
    {
      "attribute": "age_group",
      "recommendation": "adult",
      "unit": "",
      "confidence": 0.98,
      "reasoning": "Product category and description indicate adult sizing",
      "suggested_value": null
    }
  ]
}
```

- **Error Responses:**
  - `404 Not Found`: If the product key does not exist.
  - `500 Internal Server Error`: On unexpected server errors.

- **Notes:**
  - This endpoint predicts all missing attributes for the product. It does not accept a custom facet list in the request body.
  - Authentication is not currently required. (Add details here if/when implemented.)

---

### FacetPrediction Model

Each prediction in the response contains the following fields:

| Field            | Type    | Description                                                      |
|------------------|---------|------------------------------------------------------------------|
| attribute        | string  | Name of the attribute being predicted                             |
| recommendation   | string  | The recommended value for the attribute                           |
| unit             | string  | Unit of the attribute, empty string if non-numeric                |
| confidence       | float   | Confidence score (0-1) for the prediction                        |
| reasoning        | string  | Explanation for why this value was chosen                         |
| suggested_value  | string  | Suggested value if the correct value is not in the allowed list   |

---

## Planned Endpoints

The following endpoints are described for future implementation, but are **not currently available**:

#### `POST /facet-inference/predict`
Predicts labels for a single product facet, given a product and facet definition in the request body.

#### `POST /facet-inference/predict-multiple`
Predicts labels for multiple product facets concurrently, given a product and a list of facet definitions in the request body.

_See previous documentation for example request/response payloads. These endpoints are planned for future releases._

---

## Facet Inference Service

### `FacetInferenceService`

The main service class for facet inference operations. Used internally by the API to orchestrate prediction logic, data access, and LLM calls.

---

For more details on the domain models and prediction logic, see the [Core Concepts](core_concepts.md) and [Development Guide](development.md).
