# AIDA Facet Inference

A product facet inference system that uses LLMs to intelligently categorise and enrich product data. The system ingests product information and uses LLMs to infer missing facets, with confidence scoring and validation.

## Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/yourusername/aida-facet-inference.git
cd aida-facet-inference
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e ".[dev]"
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your actual values:
```bash
cp .env.example .env
# Edit .env with your settings
```

See the [Environment Variables](#environment-variables) section below for details.

### 3. Start the Database (Docker)
```bash
docker-compose --profile db up
```

### 4. Run the API Locally
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables hot-reloading for development.

### Ingest Product Data
```bash
python scripts/ingest_csvs.py --directory data
```
Ingests product data from CSV files into the database.

### Generate Product Embeddings
```bash
python scripts/embed_product_descriptions.py
```
Generates vector embeddings for all products in the database.

### Run Facet Inference
```bash
python scripts/predict_facets.py --limit 10
```
Runs facet inference for a limited number of products and stores results in the database.

For more scripts and advanced usage, see [docs/scripts.md](docs/scripts.md).

## Environment Variables

The system uses environment variables for API keys, database credentials, LLM settings, logging, CORS, rate limiting, and more. For a full list, see `.env.example` and [docs/environment_variables.md](docs/environment_variables.md).

**Critical variables to set:**
- `LLM_PROVIDER`: Choose `openai` or `azure` depending on your LLM provider
- `OPENAI_API_KEY` or `AZURE_OPENAI_API_KEY`: Your LLM API key
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database connection settings
- `API_HOST`, `API_PORT`: API server host and port
- `ALLOWED_ORIGINS`, `TRUSTED_HOSTS`: CORS and security settings for frontend/API access
- `RATE_LIMIT_REQUESTS_PER_MINUTE`: Rate limiting for API abuse prevention
- `LOG_LEVEL`: Logging verbosity
- `DEBUG`: Enable/disable debug mode

**LLM and Embedding settings:**
- `OPENAI_LLM_MODEL`, `OPENAI_EMBEDDING_MODEL`, `OPENAI_LLM_TEMPERATURE`, `OPENAI_LLM_TOP_P`, `OPENAI_LLM_FREQ_PENALTY`, `OPENAI_LLM_REASONING_EFFORT`
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_API_VERSION`
- `EMBEDDING_MIN_DIMENSIONS`, `EMBEDDING_MAX_DIMENSIONS`, `EMBEDDING_DEFAULT_DIMENSIONS`
- `OPENAI_EMBEDDING_MAX_TRIES`, `OPENAI_EMBEDDING_MAX_TIME`

See `.env.example` for all available variables and [docs/environment_variables.md](docs/environment_variables.md) for detailed explanations and advanced options. The documentation has been updated to reflect the latest configuration options and defaults.

**Never commit real secrets to version control.**

## Project Structure

```
aida-facet-inference/
├── src/
│   ├── api/                        # FastAPI endpoints
│   ├── common/                     # Shared utilities: db helpers, exceptions, file IO, logging, time
│   ├── core/                       # Core business logic
│   │   ├── performance_analysis/   # Analysis and visualization of model performance
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

## Documentation

- [Core Concepts](docs/core_concepts.md)
- [API Reference](docs/api_reference.md)
- [Development Guide](docs/development.md)
- [Architecture](docs/architecture.md)
- [Database Schema](docs/database.md)
- [Environment Variables Reference](docs/environment_variables.md)

## Development

```bash
# Run all checks
./scripts/check.sh

# Fix formatting issues
./scripts/check.sh --fix
```

## Project Goals & Next Steps

- **Refine LLM Prompts:** Continue iterative improvement of prompt templates and strategies for better facet inference accuracy and reliability. This involves systematic testing, error analysis, and prompt engineering.
- **Complete and Maintain Documentation:** Ensure all documentation is up-to-date, clear, and comprehensive, including API docs, architecture, and environment variable references.
- **Logging Improvements:** Review and enhance logging throughout the codebase for better observability, debugging, and monitoring in both development and production.
- **Refactor Full-Dataset Inference Script:** Clean up and modularize the script for running inference over large datasets, improving maintainability and testability.
- **Implement Self-Review Loop:** Add a mechanism where the model critiques and refines its own outputs, using a second LLM pass to validate or request revision, with a confidence threshold and loop cap.
- **Web Scrape Context Retrieval:** Build or integrate tooling to retrieve richer web scrape context for better citation and evidence in facet inference, leveraging LangChain or similar tools.
- **General Codebase Cleanup:** Address technical debt, improve type safety, and ensure code quality across all modules.