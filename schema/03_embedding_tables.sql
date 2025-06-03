CREATE TABLE product_embeddings (
    product_key TEXT PRIMARY KEY,
    product_description TEXT,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);