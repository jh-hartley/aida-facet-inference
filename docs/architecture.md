# Architecture

## Overview

The AIDA Facet Inference system is designed to predict product facets using LLMs. The system is built with a focus on:
- Modularity and extensibility
- Type safety
- Async operations
- Clear separation of concerns

## Core Components

### Facet Inference Module

```
src/core/facet_inference/
├── models.py          # Domain models
├── prompts.py         # LLM prompts
├── inference.py       # LLM integration
└── service.py         # Service layer
```

#### Models
- `ProductInfo`: Product data model
- `FacetDefinition`: Facet configuration
- `FacetPrediction`: Prediction results
- `ConfidenceLevel`: Confidence scoring

#### Service Layer
- Handles concurrent predictions
- Manages LLM interactions
- Provides clean async interface

### LLM Integration

```
src/core/llm/
├── client.py          # LLM client
└── models.py          # LLM models
```

- Abstracted LLM interactions
- Configurable model selection
- Structured output handling

## Data Flow

1. **Input**
   - Product information
   - Facet definitions
   - Configuration

2. **Processing**
   - Format prompt
   - Call LLM
   - Parse response

3. **Output**
   - Structured predictions
   - Confidence scores
   - Reasoning

## Design Decisions

### Async Architecture
- All I/O operations are async
- Concurrent facet predictions
- Efficient resource usage

### Type Safety
- Strict type checking
- Pydantic models
- Clear interfaces

### Prompt Engineering
- Structured prompts
- Clear examples
- Consistent formatting

### Error Handling
- Graceful failure
- Clear error messages
- Type-safe error handling

## Future Considerations

1. **Performance**
   - Caching predictions
   - Batch processing
   - Rate limiting

2. **Reliability**
   - Retry mechanisms
   - Fallback strategies
   - Monitoring

3. **Extensibility**
   - Plugin system
   - Custom models
   - Additional features 