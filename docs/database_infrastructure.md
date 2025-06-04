# Database Infrastructure

This document explains the architecture and implementation of the database infrastructure in the project. It covers the repository pattern, Postgres schema, required extensions, and how the database layer is structured and used.

---

## Overview

The database infrastructure provides robust, scalable storage for products, attributes, embeddings, predictions, and experiment metadata. It uses PostgreSQL as the backend and follows the repository pattern for data access.

- **Repository Pattern:** All database access is abstracted via repositories, enabling testability and easy backend changes.
- **Postgres Schema:** The schema is designed for extensibility, performance, and analytics, with clear separation of input, embedding, and prediction data.
- **Extensions:** Uses Postgres extensions for vector search, indexing, and similarity.

---

## Key Components

### 1. Repositories (`src/core/infrastructure/database/`)
- **Predictions:** Handles experiment and prediction result storage and retrieval.
- **Input Data:** Manages raw product, category, attribute, and value ingestion.
- **Embeddings:** Stores and retrieves product embeddings for similarity search and inference.
- All repositories are implemented as classes with clear interfaces, supporting both sync and async operations.

### 2. Postgres Schema (`schema/`)
- **Input Tables:**
  - `raw_products`, `raw_categories`, `raw_attributes`: Store product, category, and attribute metadata.
  - `raw_product_categories`, `raw_category_attributes`: Map products to categories and attributes.
  - `raw_product_attribute_values`, `raw_product_attribute_gaps`: Store attribute values and missing values (gaps).
  - `raw_category_allowable_values`, `raw_attribute_allowable_values_*`: Define allowed values for attributes by category or globally.
  - `human_recommendations`: Stores human-in-the-loop recommendations and overrides.
- **Embedding Tables:**
  - `product_embeddings`: Stores vector embeddings for products, including the embedding vector and timestamps.
- **Prediction Tables:**
  - `prediction_experiments`: Stores experiment metadata and metrics.
  - `prediction_results`: Stores individual prediction results, including confidence, reasoning, and links to recommendations.
- **Required Extensions:**
  - `vector`: For vector search and storage.
  - `btree_gin`: For efficient JSONB indexing.
  - `pg_trgm`: For trigram similarity search.

---

## Table Summaries

### Input Tables
- **raw_products:** Product metadata (key, name, code type)
- **raw_categories:** Category metadata
- **raw_attributes:** Attribute metadata (type, unit)
- **raw_product_categories:** Product-to-category mapping
- **raw_category_attributes:** Category-to-attribute mapping
- **raw_product_attribute_values:** Attribute values for products
- **raw_product_attribute_gaps:** Missing attribute values
- **raw_category_allowable_values:** Allowed values for attributes by category
- **raw_attribute_allowable_values_applicable_in_every_category:** Globally allowed values
- **raw_attribute_allowable_values_in_any_category:** Allowed in any category
- **raw_product_attribute_allowable_values:** Allowed values for a product
- **raw_recommendations:** Model-generated recommendations
- **raw_recommendation_rounds:** Recommendation batch metadata
- **raw_rich_text_sources:** Rich text sources for products
- **human_recommendations:** Human-in-the-loop recommendations and feedback

### Embedding Tables
- **product_embeddings:** Stores product embeddings (vector, description, timestamps)

### Prediction Tables
- **prediction_experiments:** Experiment metadata and metrics
- **prediction_results:** Individual prediction results (value, confidence, reasoning, correctness)

---

## Required Extensions

The following Postgres extensions must be enabled:
- `vector`: For vector storage and search
- `btree_gin`: For efficient JSONB indexing
- `pg_trgm`: For trigram similarity search

---

## Repository Pattern & Usage

- All database access is performed via repository classes in `src/core/infrastructure/database/`.
- Repositories encapsulate queries, transactions, and data mapping.
- This pattern enables easy testing, swapping of backends, and clear separation of concerns.

---

## Extending the Database Layer

- **Add a new table:** Define the schema in `schema/`, create a new repository class, and update the relevant service logic.
- **Add a new repository:** Implement the required interface and register it in the service layer.
- **Migrate schema:** Use standard SQL migration tools or manual scripts as appropriate.

---

For more details, see the code in `src/core/infrastructure/database/` and the schema files in `schema/`. 