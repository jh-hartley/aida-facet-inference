# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in the project

## API Configuration
- **API_HOST**: Host for the API server. Default is `0.0.0.0` (all interfaces). Set to `127.0.0.1` for local-only access.
- **API_PORT**: Port for the API server. Default is `8000`. Change if you have port conflicts.
- **DEBUG**: Enable debug mode (`True` or `False`). Debug mode provides more verbose error messages and auto-reload.

## CORS and Security
- **ALLOWED_ORIGINS**: Comma-separated list of allowed origins for CORS (e.g., `http://localhost:3000,http://127.0.0.1:3000`). Controls which frontends can access the API.
- **TRUSTED_HOSTS**: Comma-separated list of trusted hosts (e.g., `localhost,127.0.0.1`). Used for host header validation.
- **RATE_LIMIT_REQUESTS_PER_MINUTE**: Integer. Basic rate limiting to avoid abuse (requests per minute). Default is `60`.

## Logging
- **LOG_LEVEL**: Logging level. Valid values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Default is `INFO`.

## LLM Configuration
- **LLM_PROVIDER**: Which LLM provider to use. Valid values: `openai`, `azure`.

### OpenAI Settings (used if LLM_PROVIDER=openai)
- **OPENAI_API_KEY**: Your OpenAI API key. Required if using OpenAI.
- **OPENAI_LLM_MODEL**: OpenAI LLM model name (e.g., `gpt-4o-mini`).
- **OPENAI_EMBEDDING_MODEL**: OpenAI embedding model name (e.g., `text-embedding-3-small`).
- **OPENAI_LLM_TEMPERATURE**: Float. Controls randomness. Lower values = more deterministic. Default: `0.0`.
- **OPENAI_LLM_TOP_P**: Float. Nucleus sampling parameter. Default: `0.1`.
- **OPENAI_LLM_FREQ_PENALTY**: Float. Penalizes repeated tokens. Default: `0.0`.
- **OPENAI_LLM_REASONING_EFFORT**: String. Controls prompt complexity/effort. E.g., `high`, `medium`, `low`.

### Azure OpenAI Settings (used if LLM_PROVIDER=azure)
- **AZURE_OPENAI_API_KEY**: Your Azure OpenAI API key. Required if using Azure.
- **AZURE_OPENAI_ENDPOINT**: Azure OpenAI endpoint URL. E.g., `https://your-azure-endpoint.openai.azure.com`.
- **AZURE_OPENAI_API_VERSION**: API version string. E.g., `2024-02-15-preview`.
- **AZURE_OPENAI_DEPLOYMENT**: Azure OpenAI deployment name (e.g., `gpt-4o-mini`).
- **AZURE_OPENAI_EMBEDDING_DEPLOYMENT**: Azure embedding deployment name (e.g., `text-embedding-ada-002`).
- **AZURE_OPENAI_EMBEDDING_API_VERSION**: API version for Azure embedding deployment (e.g., `2023-05-15`).

## Embedding Configuration
- **EMBEDDING_MIN_DIMENSIONS**: Integer. Minimum embedding dimensions. Default: `1536`.
- **EMBEDDING_MAX_DIMENSIONS**: Integer. Maximum embedding dimensions. Default: `1536`.
- **EMBEDDING_DEFAULT_DIMENSIONS**: Integer. Default embedding dimensions. Default: `1536`.
- **OPENAI_EMBEDDING_MAX_TRIES**: Integer. Max tries for embedding model before failing. Default: `10`.
- **OPENAI_EMBEDDING_MAX_TIME**: Integer (seconds). Max time for embedding model before timeout. Default: `120`.

## Database Configuration
- **DB_HOST**: Database host (e.g., `localhost`).
- **DB_PORT**: Database port (e.g., `5432`).
- **DB_NAME**: Database name.
- **DB_USER**: Database user.
- **DB_PASSWORD**: Database password.
- **DB_USE_SSL**: Use SSL for DB connection (`True` or `False`). Default: `False` for local dev.
- **DB_POOL_SIZE**: SQLAlchemy pool size. Default: `5`.
- **DB_MAX_OVERFLOW**: SQLAlchemy max overflow. Default: `2`.
- **DB_ASYNC_POOL_SIZE**: SQLAlchemy async pool size. Default: `20`.

## Vector Database (Optional)
- **VECTOR_DB_URL**: URL for the vector database service.
- **VECTOR_DB_API_KEY**: API key for the vector database.

## App Settings (Optional)
- **ENV**: Application environment (e.g., `development`, `production`).

## Notes
- All variables above are shown in `.env.example` with example values or defaults.
- If you add new environment variables, document them here and in `.env.example`.