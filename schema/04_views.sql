CREATE MATERIALIZED VIEW IF NOT EXISTS product_summary AS
SELECT 
    p.id,
    p.name,
    p.identifier_value,
    p.identifier_type,
    p.category,
    r.name as retailer_name,
    rp.price,
    rp.availability,
    rp.url as retailer_url
FROM products p
JOIN retailer_products rp ON p.id = rp.product_id
JOIN retailers r ON rp.retailer_id = r.id; 