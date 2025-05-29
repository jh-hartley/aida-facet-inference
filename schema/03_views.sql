CREATE MATERIALIZED VIEW IF NOT EXISTS product_summary AS
SELECT 
    rp.product_key,
    rp.friendly_name as name,
    rp.system_name,
    rpc.category_key,
    rc.friendly_name as category_name,
    rpav.attribute_key,
    rpav.value as attribute_value,
    ra.attribute_type,
    ra.unit_measure_type
FROM raw_products rp
LEFT JOIN raw_product_categories rpc ON rp.product_key = rpc.product_key
LEFT JOIN raw_categories rc ON rpc.category_key = rc.category_key
LEFT JOIN raw_product_attribute_values rpav ON rp.product_key = rpav.product_key
LEFT JOIN raw_attributes ra ON rpav.attribute_key = ra.attribute_key; 