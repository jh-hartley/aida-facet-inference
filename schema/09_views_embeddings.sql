-- Product similarity search view
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_views WHERE viewname = 'product_similarity_search'
    ) THEN
        CREATE VIEW product_similarity_search AS
        SELECT 
            p1.product_key,
            p2.product_key AS similar_product_key,
            1 - (p1.embedding <=> p2.embedding) AS similarity_score
        FROM product_embeddings p1
        CROSS JOIN product_embeddings p2
        WHERE p1.product_key != p2.product_key;
    END IF;
END $$;

-- Embedding statistics view
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_views WHERE viewname = 'embedding_stats'
    ) THEN
        CREATE VIEW embedding_stats AS
        SELECT 
            'product' AS entity_type,
            COUNT(*) AS total_embeddings,
            MIN(created_at) AS oldest_embedding,
            MAX(created_at) AS newest_embedding
        FROM product_embeddings;
    END IF;
END $$; 