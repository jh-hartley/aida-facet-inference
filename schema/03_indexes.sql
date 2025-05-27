CREATE INDEX IF NOT EXISTS idx_products_identifier ON products(identifier_type, identifier_value);
CREATE INDEX IF NOT EXISTS idx_products_attributes ON products USING gin(attributes);

CREATE INDEX IF NOT EXISTS idx_product_embeddings_embedding ON product_embeddings USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_product_summary_identifier ON product_summary(identifier_type, identifier_value);
CREATE INDEX IF NOT EXISTS idx_product_summary_retailer ON product_summary(retailer_name); 