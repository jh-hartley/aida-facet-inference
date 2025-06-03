-- Vector similarity indexes
CREATE INDEX IF NOT EXISTS idx_product_embeddings_embedding ON product_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_product_embeddings_created_at ON product_embeddings(created_at);