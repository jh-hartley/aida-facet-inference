# Architecture

## Project Structure Overview```
aida-facet-inference/
├── src/
│   ├── api/                        # FastAPI endpoints
│   ├── common/                     # Shared utilities: db helpers, exceptions, file IO, logging, time
│   ├── core/                       # Core business logic
│   │   ├── performance_analysis/   # Analysis and visualisation of model performance
│   │   ├── domain/                 # Domain models, confidence logic, product identifiers, repository interfaces, type definitions
│   │   ├── similarity_search/      # Similarity search logic and models
│   │   ├── csv_ingestion/          # CSV ingestion logic, processors, and unit-of-work
│   │   ├── prompts/                # Prompt management and templates
│   │   ├── embedding_generation/   # Embedding generation logic and jobs
│   │   ├── facet_inference/        # Facet inference logic, orchestration, and components
│   │   ├── data_analysis/          # Data analysis tools and loaders
│   │   └── infrastructure/         # Integrations: LLM (OpenAI, Azure), database repositories, embeddings, input data, predictions
│   │       ├── llm/                # LLM provider clients, models, utilities, and provider-specific implementations
│   │       └── database/           # Database access, repositories for predictions, input data, embeddings
│   └── main.py                     # Application entry point
├── scripts/                        # Utility and data scripts
├── tests/                          # Test suite
├── docs/                           # Detailed documentation
├── schema/                         # Database schema (SQL)
├── hooks/                          # Git hooks and related scripts
├── .github/                        # GitHub workflows and configs
├── data/                           # Example and test data
├── Dockerfile.api                  # Dockerfile for API
├── docker-compose.yml              # Docker Compose config
├── pyproject.toml                  # Python project config
├── .env.example                    # Example environment variables
└── README.md                       # Project overview and setup
```

---

## Layered Architecture & DDD Approach

The system is organised into layers, each with distinct responsibilities:

- **API Layer (`src/api/`)**: Exposes HTTP endpoints using FastAPI. Handles request/response DTOs, input validation, and routing.
- **Core Layer (`src/core/`)**: Contains all business logic, organised by domain concepts. Implements services, domain models, and orchestration.
- **Infrastructure Layer (`src/core/infrastructure/`)**: Integrates with external systems (LLMs, databases). Implements provider-specific logic and repository patterns.
- **Common Utilities (`src/common/`)**: Shared helpers for DB access, error handling, logging, and file IO.

**Domain-Driven Design (DDD) Principles:**
- **Domain Models**: Central business objects (e.g., Product, Facet, Prediction) live in `core/domain`.
- **Repositories**: Abstract data access, implemented in infrastructure.
- **Services**: Orchestrate business logic, often async and stateless.
- **Value Objects & Types**: Used for strong typing and invariants.

---

## Section-by-Section Breakdown

### API Layer (`src/api/`)
- **Routers**: Define HTTP endpoints (e.g., `/facet-inference/predict/{product_key}`) and group related routes.
- **DTOs**: Pydantic models for request/response validation, decoupled from domain models.
- **Dependency Injection**: Uses FastAPI's dependency system for DB sessions and service wiring.

### Core Layer (`src/core/`)
- **domain/**: Domain models, confidence logic, product identifiers, repository interfaces, and type definitions. Implements DDD patterns.
- **facet_inference/**: Main business logic for facet prediction. Includes service layer, orchestration, concurrency management, and prediction components.
- **embedding_generation/**: Logic for generating and managing vector embeddings, including jobs and unit-of-work patterns.
- **similarity_search/**: Implements similarity search over embeddings, with caching and service abstractions.
- **csv_ingestion/**: Handles CSV ingestion, parsing, and batch processing using processors and UoW.
- **prompts/**: Manages prompt templates and prompt engineering for LLMs.
- **performance_analysis/**: Tools and scripts for analysing and visualising model performance.
- **data_analysis/**: Data loaders and evaluators for ground truth and prediction analysis.

### Infrastructure Layer (`src/core/infrastructure/`)
- **llm/**: Provider-agnostic LLM client, with submodules for OpenAI, Azure, and utilities. Handles prompt invocation and model selection.
- **database/**: Implements repository patterns for predictions, input data, and embeddings. Encapsulates all DB access.

### Common Utilities (`src/common/`)
- **db.py**: DB session management and helpers.
- **exceptions.py**: Custom error types.
- **read_files.py**: File IO utilities.
- **clock.py**: Time utilities.
- **logs/**: Logging configuration and helpers.

### Scripts (`scripts/`)
- Utility scripts for embedding, prediction, ingestion, and checks. Used for operational tasks and automation.

### Tests (`tests/`)
- Test suite for unit, integration, and end-to-end testing. Organised to mirror the main codebase structure.

---

## Data Flow Diagrams

### HTTP Request Flow
```
Client Request
→ API Endpoint (FastAPI)
→ Request DTO Validation
→ Service Layer (core)
→ LLM/DB/Embedding Processing
→ Response DTO
→ Client Response
```

### Facet Inference Flow
```
Product Key
→ FacetInferenceService
→ ProductFacetPredictor
→ LLM Processing
→ Confidence Scoring
→ FacetPrediction
```

---

## Design Decisions & Patterns

- **Async-First Design**: All service and prediction logic is async for scalability.
- **Separation of Concerns**: API, business logic, and infrastructure are strictly separated.
- **Repository Pattern**: All data access is abstracted via repositories, enabling easy swapping of DB backends.
- **Service Layer**: Orchestrates business logic, keeps controllers thin.
- **Unit of Work (UoW)**: Used in batch operations (e.g., CSV ingestion, embedding jobs) for transactional integrity.
- **Dependency Injection**: Used throughout for testability and flexibility.
- **Extensibility**: New LLM providers, embedding models, or business logic can be added with minimal changes to existing code.

---

## Extending the System

- **Adding a New LLM Provider**: Implement a new provider in `infrastructure/llm/providers/` and register it in the LLM client.
- **Adding a New API Endpoint**: Create a new router in `api/routers/` and wire up the service layer.
- **Adding New Business Logic**: Place new domain logic in `core/domain/` or a new submodule under `core/` as appropriate.
- **Adding New Data Pipelines**: Use the UoW and repository patterns for robust, testable data processing.

---

## Future Considerations

- **API Enhancements**: Authentication, rate limiting, request validation middleware, API versioning.
- **Performance**: Caching, batch processing, connection pooling, response compression.
- **Monitoring**: Request logging, performance metrics, error tracking, usage analytics.
- **Self-Review Loop**: Planned mechanism for LLM self-critique and output refinement.
- **Web Scrape Context Retrieval**: Planned integration for richer product context.

---

For more details, see the [Core Concepts](core_concepts.md), [API Reference](api_reference.md), [Development Guide](development.md), and [Environment Variables Reference](environment_variables.md). 

