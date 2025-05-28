# Architecture

## System Overview

The AIDA Facet Inference system is built with a clean, modular architecture that separates concerns and promotes maintainability. The system consists of several key components:

1. **API Layer** (`src/api/`)
   - FastAPI-based HTTP endpoints
   - Request/response DTOs
   - Input validation
   - Route handling

2. **Core Layer** (`src/core/`)
   - Business logic implementation
   - Facet inference service
   - LLM integration
   - Model definitions

3. **Database Layer** (`src/db/`)
   - Database operations
   - Connection management
   - Query handling

4. **Utility Layer** (`src/utils/`)
   - Shared utilities
   - Helper functions
   - Common types

## Data Flow

1. **HTTP Request Flow**
   ```
   Client Request
   → API Endpoint
   → Request DTO Validation
   → Service Layer
   → LLM Processing
   → Response DTO
   → Client Response
   ```

2. **Facet Inference Flow**
   ```
   Product Info + Facet Definition
   → FacetInferenceService
   → ProductFacetPredictor
   → LLM Processing
   → Confidence Scoring
   → FacetPrediction
   ```

## Design Decisions

1. **API Design**
   - RESTful endpoints for facet inference
   - Async processing for concurrent predictions
   - Pydantic models for request/response validation
   - Clear separation between API and business logic

2. **Service Layer**
   - Dependency injection for flexibility
   - Async-first design for performance
   - Clear interfaces for testing
   - Modular predictor implementation

3. **LLM Integration**
   - Abstracted LLM interface
   - Configurable model selection
   - Structured prompt management
   - Confidence scoring system

## Future Considerations

1. **API Enhancements**
   - Authentication/authorization
   - Rate limiting
   - Request validation middleware
   - API versioning

2. **Performance**
   - Caching layer
   - Batch processing optimization
   - Connection pooling
   - Response compression

3. **Monitoring**
   - Request logging
   - Performance metrics
   - Error tracking
   - Usage analytics 