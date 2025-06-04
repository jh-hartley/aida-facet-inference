# Environment Variables Reference

This document lists and explains all environment variables used in the AIDA Facet Inference project. Use this as a reference when configuring your `.env` file.

## API Configuration
- **API_HOST**: Host for the API server (default: `0.0.0.0`).
- **API_PORT**: Port for the API server (default: `8000`).
- **DEBUG**: Enable debug mode (`True` or `False`).

## CORS and Security
- **ALLOWED_ORIGINS**: Comma-separated list of allowed origins for CORS (e.g., `http://localhost:3000,http://127.0.0.1:3000`).
- **TRUSTED_HOSTS**: Comma-separated list of trusted hosts (e.g., `localhost,127.0.0.1`).
- **RATE_LIMIT_REQUESTS_PER_MINUTE**: Basic rate limiting to avoid abuse (requests per minute).

## Logging
- **LOG_LEVEL**: Logging level (e.g., `INFO`, `DEBUG`).

## LLM Configuration
- **LLM_PROVIDER**: Choose `openai` or `azure` depending on the provider in use.

### OpenAI Settings (used if LLM_PROVIDER=openai)
- **OPENAI_API_KEY**: Your OpenAI API key.
- **OPENAI_LLM_MODEL**: OpenAI LLM model name (e.g., `gpt-4o-mini`).
- **OPENAI_EMBEDDING_MODEL**: OpenAI embedding model name (e.g., `text-embedding-3-small`).
- **OPENAI_LLM_TEMPERATURE**: LLM temperature (e.g., `0.0`).
- **OPENAI_LLM_TOP_P**: LLM top_p (e.g., `0.1`).
- **OPENAI_LLM_FREQ_PENALTY**: LLM frequency penalty (e.g., `0.0`).
- **OPENAI_LLM_REASONING_EFFORT**: LLM reasoning effort (e.g., `high`).

### Azure OpenAI Settings (used if LLM_PROVIDER=azure)
- **AZURE_OPENAI_API_KEY**: Your Azure OpenAI API key.
- **AZURE_OPENAI_ENDPOINT**: Azure OpenAI endpoint URL.
- **AZURE_OPENAI_API_VERSION**: Azure OpenAI API version (e.g., `2024-02-15-preview`).
- **AZURE_OPENAI_DEPLOYMENT**: Azure OpenAI deployment name (e.g., `gpt-4o-mini`).
- **AZURE_OPENAI_EMBEDDING_DEPLOYMENT**: Azure embedding deployment name (e.g., `text-embedding-3-small`).

## Embedding Configuration
- **EMBEDDING_MIN_DIMENSIONS**: Minimum embedding dimensions (e.g., `1536`).
- **EMBEDDING_MAX_DIMENSIONS**: Maximum embedding dimensions (e.g., `1536`).
- **EMBEDDING_DEFAULT_DIMENSIONS**: Default embedding dimensions (e.g., `1536`).
- **OPENAI_EMBEDDING_MAX_TRIES**: Max tries for embedding model (e.g., `5`).
- **OPENAI_EMBEDDING_MAX_TIME**: Max time for embedding model in seconds (e.g., `60`).

## Database Configuration
- **DB_HOST**: Database host (e.g., `localhost`).
- **DB_PORT**: Database port (e.g., `5432`).
- **DB_NAME**: Database name.
- **DB_USER**: Database user.
- **DB_PASSWORD**: Database password.
- **DB_USE_SSL**: Use SSL for DB connection (`True` or `False`).
- **DB_POOL_SIZE**: SQLAlchemy pool size (e.g., `5`).
- **DB_MAX_OVERFLOW**: SQLAlchemy max overflow (e.g., `2`).
- **DB_ASYNC_POOL_SIZE**: SQLAlchemy async pool size (e.g., `20`).

## Vector Database
- **VECTOR_DB_URL**: URL for the vector database service.
- **VECTOR_DB_API_KEY**: API key for the vector database.

## App Settings
- **ENV**: Application environment (e.g., `development`, `production`).

## Adding New Variables
If you add new environment variables, document them here and in `.env.example`. 