-- Similarity search view for products
CREATE VIEW IF NOT EXISTS product_similarity_search AS
SELECT 
    p1.product_key,
    p2.product_key AS similar_product_key,
    1 - (p1.embedding <=> p2.embedding) AS similarity_score
FROM product_embeddings p1
CROSS JOIN product_embeddings p2
WHERE p1.product_key != p2.product_key;

-- Embedding statistics view
CREATE VIEW IF NOT EXISTS embedding_stats AS
SELECT 
    'product' AS entity_type,
    COUNT(*) AS total_embeddings,
    MIN(created_at) AS oldest_embedding,
    MAX(created_at) AS newest_embedding
FROM product_embeddings
UNION ALL
SELECT 
    'attribute' AS entity_type,
    COUNT(*) AS total_embeddings,
    MIN(created_at) AS oldest_embedding,
    MAX(created_at) AS newest_embedding
FROM attribute_embeddings
UNION ALL
SELECT 
    'category' AS entity_type,
    COUNT(*) AS total_embeddings,
    MIN(created_at) AS oldest_embedding,
    MAX(created_at) AS newest_embedding
FROM category_embeddings
UNION ALL
SELECT 
    'value' AS entity_type,
    COUNT(*) AS total_embeddings,
    MIN(created_at) AS oldest_embedding,
    MAX(created_at) AS newest_embedding
FROM value_embeddings; 