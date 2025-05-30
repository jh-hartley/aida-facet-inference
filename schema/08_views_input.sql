-- Product summary view combining products, categories, and attributes
CREATE MATERIALIZED VIEW IF NOT EXISTS product_summary AS
SELECT 
    p.product_key,
    p.system_name AS product_system_name,
    p.friendly_name AS product_friendly_name,
    c.category_key,
    c.system_name AS category_system_name,
    c.friendly_name AS category_friendly_name,
    a.attribute_key,
    a.system_name AS attribute_system_name,
    a.friendly_name AS attribute_friendly_name,
    a.attribute_type,
    a.unit_measure_type,
    pav.value AS attribute_value,
    r.value AS recommended_value,
    r.confidence AS recommendation_confidence,
    r.created_at AS recommendation_created_at
FROM raw_products p
LEFT JOIN raw_product_categories pc ON p.product_key = pc.product_key
LEFT JOIN raw_categories c ON pc.category_key = c.category_key
LEFT JOIN raw_category_attributes ca ON c.category_key = ca.category_key
LEFT JOIN raw_attributes a ON ca.attribute_key = a.attribute_key
LEFT JOIN raw_product_attribute_values pav ON p.product_key = pav.product_key AND a.attribute_key = pav.attribute_key
LEFT JOIN raw_recommendations r ON p.product_key = r.product_key AND a.attribute_key = r.attribute_key;

-- Create a unique index on the materialized view for concurrent refreshes
CREATE UNIQUE INDEX IF NOT EXISTS product_summary_unique_idx ON product_summary (product_key, category_key, attribute_key);

-- Attribute value statistics view
CREATE VIEW IF NOT EXISTS attribute_value_stats AS
SELECT 
    a.attribute_key,
    a.system_name AS attribute_system_name,
    a.friendly_name AS attribute_friendly_name,
    COUNT(DISTINCT pav.value) AS unique_values_count,
    COUNT(DISTINCT pav.product_key) AS products_with_value_count,
    COUNT(DISTINCT r.value) AS unique_recommendations_count
FROM raw_attributes a
LEFT JOIN raw_product_attribute_values pav ON a.attribute_key = pav.attribute_key
LEFT JOIN raw_recommendations r ON a.attribute_key = r.attribute_key
GROUP BY a.attribute_key, a.system_name, a.friendly_name;

-- Product details view for quick access to complete product information
CREATE MATERIALIZED VIEW IF NOT EXISTS product_details AS
SELECT 
    p.product_key,
    p.system_name AS product_system_name,
    p.friendly_name AS product_friendly_name,
    array_agg(DISTINCT c.friendly_name) AS categories,
    jsonb_agg(
        DISTINCT jsonb_build_object(
            'attribute', a.friendly_name,
            'value', pav.value
        )
    ) AS attributes,
    jsonb_agg(
        DISTINCT jsonb_build_object(
            'descriptor', rt.name,
            'value', rt.content
        ) ORDER BY rt.priority
    ) AS descriptions
FROM raw_products p
LEFT JOIN raw_product_categories pc ON p.product_key = pc.product_key
LEFT JOIN raw_categories c ON pc.category_key = c.category_key
LEFT JOIN raw_product_attribute_values pav ON p.product_key = pav.product_key
LEFT JOIN raw_attributes a ON pav.attribute_key = a.attribute_key
LEFT JOIN raw_rich_text_sources rt ON p.product_key = rt.product_key
GROUP BY p.product_key, p.system_name, p.friendly_name;

-- Create a unique index on the materialized view
CREATE UNIQUE INDEX IF NOT EXISTS product_details_unique_idx ON product_details (product_key);

-- Product gaps view for quick access to missing attributes and their allowable values
CREATE MATERIALIZED VIEW IF NOT EXISTS product_gaps AS
WITH allowable_values AS (
    SELECT 
        attribute_key,
        array_agg(DISTINCT value) AS values
    FROM (
        SELECT attribute_key, value FROM raw_category_allowable_values
        UNION
        SELECT attribute_key, value FROM raw_attribute_allowable_values_applicable_in_every_category
        UNION
        SELECT attribute_key, value FROM raw_attribute_allowable_values_in_any_category
    ) combined_values
    GROUP BY attribute_key
)
SELECT 
    p.product_key,
    p.friendly_name AS product_friendly_name,
    a.attribute_key,
    a.friendly_name AS attribute_friendly_name,
    av.values AS allowable_values
FROM raw_products p
JOIN raw_product_attribute_gaps pag ON p.product_key = pag.product_key
JOIN raw_attributes a ON pag.attribute_key = a.attribute_key
LEFT JOIN allowable_values av ON a.attribute_key = av.attribute_key;

-- Create a unique index on the materialized view
CREATE UNIQUE INDEX IF NOT EXISTS product_gaps_unique_idx ON product_gaps (product_key, attribute_key); 