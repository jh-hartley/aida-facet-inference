# Scripts Reference

This document provides an overview of the main utility scripts available in the `scripts/` directory. These scripts are used for data ingestion, embedding generation, and running facet inference experiments.

---

## scripts/ingest_csvs.py
- **Purpose:**
  Ingests product data from CSV files into the database.
- **Usage:**
  ```bash
  python scripts/ingest_csvs.py [--directory <dir>] [--batch-size <n>] [--row-limit <n>] [--code-type <type>] [--debug]
  ```
- **Arguments:**
  - `--directory`: Directory containing CSV files (default: `data`)
  - `--batch-size`: Number of rows to process in each batch (default: `1000`)
  - `--row-limit`: Maximum number of rows to process per file (default: no limit)
  - `--code-type`: Force a specific code type for all products (default: auto-detect)
  - `--debug`: Enable debug logging
- **Example:**
  ```bash
  python scripts/ingest_csvs.py --directory data --batch-size 500
  ```
- **Notes:**
  - Requires the database to be running and environment variables to be set.
  - Supports batch and partial ingestion for large datasets.

---

## scripts/embed_product_descriptions.py
- **Purpose:**
  Generates vector embeddings for product descriptions and stores them in the database.
- **Usage:**
  ```bash
  python scripts/embed_product_descriptions.py [--product <PRODUCT_KEY>] [--max-concurrency <n>]
  ```
- **Arguments:**
  - `--product`: Product key to embed (if omitted, embeds all products)
  - `--max-concurrency`: Maximum number of concurrent embedding jobs (default: `32`)
- **Examples:**
  ```bash
  python scripts/embed_product_descriptions.py
  python scripts/embed_product_descriptions.py --product 123e4567-e89b-12d3-a456-426614174000
  ```
- **Notes:**
  - Embeddings are generated using the configured LLM provider and stored in the database.
  - Can be run for all products or a single product.

---

## scripts/predict_facets.py
- **Purpose:**
  Runs a facet inference experiment, predicting missing facets for products and storing results.
- **Usage:**
  ```bash
  python scripts/predict_facets.py [--description <desc>] [--limit <n>] [--product <PRODUCT_KEY>]
  ```
- **Arguments:**
  - `--description`: Description of the experiment (for logging/metadata)
  - `--limit`: Limit the number of products to process (default: all)
  - `--product`: Run experiment for a single product key
- **Examples:**
  ```bash
  python scripts/predict_facets.py --limit 10
  python scripts/predict_facets.py --product 123e4567-e89b-12d3-a456-426614174000
  ```
- **Notes:**
  - Results are stored in the database and include experiment metadata.
  - Can be run for all products, a limited number, or a single product.

---

For additional scripts and advanced usage, see the `scripts/` directory and script docstrings. 