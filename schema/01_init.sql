-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    ean TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create facets table
CREATE TABLE IF NOT EXISTS facets (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create product_facets table (junction table)
CREATE TABLE IF NOT EXISTS product_facets (
    product_id INTEGER REFERENCES products(id),
    facet_id INTEGER REFERENCES facets(id),
    value TEXT NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, facet_id)
);

-- Create vector embeddings table
CREATE TABLE IF NOT EXISTS product_embeddings (
    product_id INTEGER PRIMARY KEY REFERENCES products(id),
    embedding vector(1536),  -- OpenAI's embedding dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
); 