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

## Environment Variables

The system uses environment variables for API keys, database credentials, LLM settings, logging, and more. See `.env.example` for a full list. Key variables include:

### API Configuration
- `API_HOST`: Host for the API server (default: `0.0.0.0`)
- `API_PORT`: Port for the API server (default: `8000`)
- `DEBUG`: Enable debug mode (`True` or `False`)

### CORS and Security
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS
- `TRUSTED_HOSTS`: Comma-separated list of trusted hosts
- `RATE_LIMIT_REQUESTS_PER_MINUTE`: Basic rate limiting (requests per minute)

### Logging
- `LOG_LEVEL`: Logging level (e.g., `INFO`, `DEBUG`)

### LLM Configuration
- `LLM_PROVIDER`: Choose `openai` or `azure`
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_LLM_MODEL`: OpenAI LLM model name
- `OPENAI_EMBEDDING_MODEL`: OpenAI embedding model name
- `OPENAI_LLM_TEMPERATURE`: LLM temperature
- `OPENAI_LLM_TOP_P`: LLM top_p
- `OPENAI_LLM_FREQ_PENALTY`: LLM frequency penalty
- `OPENAI_LLM_REASONING_EFFORT`: LLM reasoning effort
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_VERSION`: Azure OpenAI API version
- `AZURE_OPENAI_DEPLOYMENT`: Azure OpenAI deployment name
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Azure embedding deployment name

### Embedding Configuration
- `EMBEDDING_MIN_DIMENSIONS`: Minimum embedding dimensions
- `EMBEDDING_MAX_DIMENSIONS`: Maximum embedding dimensions
- `EMBEDDING_DEFAULT_DIMENSIONS`: Default embedding dimensions
- `OPENAI_EMBEDDING_MAX_TRIES`: Max tries for embedding model
- `OPENAI_EMBEDDING_MAX_TIME`: Max time for embedding model (seconds)

### Database Configuration
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_USE_SSL`: Use SSL for DB connection (`True` or `False`)
- `DB_POOL_SIZE`: SQLAlchemy pool size
- `DB_MAX_OVERFLOW`: SQLAlchemy max overflow
- `DB_ASYNC_POOL_SIZE`: SQLAlchemy async pool size

**Never commit real secrets to version control.**

## Project Structure

```
aida-facet-inference/
├── src/
│   ├── api/                    # FastAPI endpoints
│   ├── core/                   # Core business logic
│   │   ├── facet_inference/    # Facet inference implementation
│   │   └── llm/                # LLM integration
│   ├── db/                     # Database operations
│   ├── utils/                  # Utility functions
│   └── main.py                 # Application entry point
├── tests/                      # Test suite
├── docs/                       # Detailed documentation
└── scripts/                    # Utility scripts
```

## Documentation

- [Core Concepts](docs/core_concepts.md)
- [API Reference](docs/api_reference.md)
- [Development Guide](docs/development.md)
- [Architecture](docs/architecture.md)
- [Database Schema](docs/database.md)
- [Environment Variables Reference](docs/README_env_vars.md)

## Development

```bash
# Run all checks
./scripts/check.sh

# Fix formatting issues
./scripts/check.sh --fix
```

## Project Goals & Next Steps

- Refine prompts for LLMs
- Finish and maintain documentation
- Clean up logging and the full-dataset inference script
- Introduce a self-review loop for model outputs
- Build richer web scrape context retrieval tooling