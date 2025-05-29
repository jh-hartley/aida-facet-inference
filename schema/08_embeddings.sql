CREATE TABLE product_embeddings (
    id SERIAL PRIMARY KEY,
    product_key TEXT REFERENCES raw_products(product_key),
    embedding_model TEXT NOT NULL,  -- e.g., 'openai-ada-002'
    embedding vector(1536),  -- Adjust dimension based on model
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_key, embedding_model)
);

CREATE INDEX IF NOT EXISTS idx_product_embeddings_embedding ON product_embeddings USING ivfflat (embedding vector_cosine_ops); 