-- Vector similarity indexes
CREATE INDEX IF NOT EXISTS idx_product_embeddings_embedding ON product_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_attribute_embeddings_embedding ON attribute_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_category_embeddings_embedding ON category_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_value_embeddings_embedding ON value_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Timestamp indexes for tracking updates
CREATE INDEX IF NOT EXISTS idx_product_embeddings_created_at ON product_embeddings(created_at);
CREATE INDEX IF NOT EXISTS idx_attribute_embeddings_created_at ON attribute_embeddings(created_at);
CREATE INDEX IF NOT EXISTS idx_category_embeddings_created_at ON category_embeddings(created_at);
CREATE INDEX IF NOT EXISTS idx_value_embeddings_created_at ON value_embeddings(created_at); 