# API Reference

## HTTP API Endpoints

### Facet Inference Endpoints

#### `POST /facet-inference/predict`

Predicts labels for a single product facet.

**Request Body:**
```json
{
    "product": {
        "ean": "1234567890123",  // 13-digit EAN
        "name": "Product Name",
        "description": "Product Description",
        "category": "Product Category",
        "attributes": {
            "key": "value"
        }
    },
    "facet": {
        "name": "gender",
        "acceptable_labels": ["mens", "womens", "unisex"],
        "allow_multiple": false,
        "is_nullable": false
    }
}
```

**Response:**
```json
{
    "prediction": {
        "facet_name": "gender",
        "labels": ["mens"],
        "confidence": 0.95,
        "reasoning": "Product description indicates this is a men's item",
        "suggested_label": null
    }
}
```

#### `POST /facet-inference/predict-multiple`

Predicts labels for multiple product facets concurrently.

**Request Body:**
```json
{
    "product": {
        "ean": "1234567890123",
        "name": "Product Name",
        "description": "Product Description",
        "category": "Product Category",
        "attributes": {
            "key": "value"
        }
    },
    "facets": [
        {
            "name": "gender",
            "acceptable_labels": ["mens", "womens", "unisex"],
            "allow_multiple": false,
            "is_nullable": false
        },
        {
            "name": "age_group",
            "acceptable_labels": ["adult", "child"],
            "allow_multiple": false,
            "is_nullable": false
        }
    ]
}
```

**Response:**
```json
{
    "predictions": [
        {
            "facet_name": "gender",
            "labels": ["mens"],
            "confidence": 0.95,
            "reasoning": "Product description indicates this is a men's item",
            "suggested_label": null
        },
        {
            "facet_name": "age_group",
            "labels": ["adult"],
            "confidence": 0.98,
            "reasoning": "Product category and description indicate adult sizing",
            "suggested_label": null
        }
    ]
}
```

## Facet Inference Service

### `FacetInferenceService`

The main service class for facet inference operations.

```