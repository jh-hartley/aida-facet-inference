# Embedding Generation

This document explains how embeddings are generated, configured, stored, and used in the system, including code examples and guidance for extending embedding support.

---

## Overview

Embeddings are high-dimensional vector representations of product descriptions, used for similarity search, inference, and recommendations. The system supports multiple embedding providers (OpenAI, Azure) and uses the `pgvector` extension in PostgreSQL for efficient storage and similarity search.

---

## Supported Embedding Models and Providers

- **Providers:** OpenAI, Azure OpenAI (configurable via environment variables)
- **Models:** Configurable (e.g., `text-embedding-3-small`, `text-embedding-ada-002`)
- **Selection:** The active provider and model are set via environment variables:
  - `LLM_PROVIDER`
  - `OPENAI_EMBEDDING_MODEL`
  - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`

---

## Configuration Options

Key environment variables for embedding configuration:
- `LLM_PROVIDER`: `openai` or `azure`
- `OPENAI_EMBEDDING_MODEL`: e.g., `text-embedding-3-small`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: e.g., `text-embedding-ada-002`
- `EMBEDDING_DEFAULT_DIMENSIONS`: e.g., `1536`
- `OPENAI_EMBEDDING_MAX_TRIES`, `OPENAI_EMBEDDING_MAX_TIME`: Retry/backoff settings

See [docs/environment_variables.md](environment_variables.md) for full details.

---

## How Embeddings Are Generated

- Product descriptions are constructed from product metadata, attributes, and rich text sources.
- Descriptions are tokenized and, if necessary, chunked to fit model limits.
- Each chunk is embedded using the configured provider/model.
- If chunked, embeddings are averaged (weighted by chunk length) and normalized.
- Embeddings are stored in the `product_embeddings` table in PostgreSQL.

### Code Example: Generating and Storing an Embedding

```python
from src.core.embedding_generation.uow.create_embedding import create_embedding

# Generate and store an embedding for a product
embedding = await create_embedding(product_key, product_description)
```

### Code Example: Batch Embedding

```python
from src.core.embedding_generation.jobs.embed_product_descriptions import create_embeddings_for_products

# Generate embeddings for all products (with concurrency)
await create_embeddings_for_products(max_concurrency=10)
```

---

## Embedding Storage and Retrieval

- Embeddings are stored in the `product_embeddings` table as `vector(1536)` columns (using pgvector).
- The repository pattern is used for all database access:
  - `ProductEmbeddingRepository` handles creation, update, retrieval, and similarity search.
- Embeddings are versioned with `created_at` and `updated_at` timestamps.

### Code Example: Retrieving an Embedding

```python
from src.core.infrastructure.database.embeddings.repository import ProductEmbeddingRepository

repo = ProductEmbeddingRepository(session)
embedding = repo.find(product_key)
```

---

## Similarity Search

- The system uses pgvector's `ivfflat` index for fast nearest-neighbor search.
- Similarity queries can be performed by product key or by embedding vector.
- Example method: `find_similar_products_by_key(product_key, limit=10, distance_threshold=0.3)`

---

## Adding New Embedding Models

1. **Update Configuration:**
   - Add the new model name to your environment variables.
   - Update `EMBEDDING_DEFAULT_DIMENSIONS` if the new model uses a different vector size.

2. **Provider Support:**
   - Ensure the provider's client supports the new model.
   - If using a new provider, implement a new embedding client in `src/core/infrastructure/llm/providers/`.

3. **Update Model Selection Logic:**
   - Update `get_current_embedding_model_name()` and related logic in `generators.py` if needed.

4. **Test:**
   - Run embedding generation and verify embeddings are created and stored as expected.

---

## Design Patterns & Best Practices

- **Repository Pattern:** All embedding storage and retrieval is abstracted for testability and flexibility.
- **Async/Await:** Embedding generation is async to support high throughput and concurrency.
- **Backoff/Retry:** Handles rate limits and transient errors from providers.
- **Normalization:** Embeddings are normalized for consistent similarity scoring.

---

For more details, see the code in `src/core/embedding_generation/` and `src/core/infrastructure/database/embeddings/`. 