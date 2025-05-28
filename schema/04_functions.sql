CREATE OR REPLACE FUNCTION create_retailer_partitions()
RETURNS TRIGGER AS $$
BEGIN
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS retailer_products_%s PARTITION OF retailer_products FOR VALUES IN (%s)',
        NEW.id, NEW.id
    );
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS retailer_product_attributes_%s PARTITION OF retailer_product_attributes FOR VALUES IN (%s)',
        NEW.id, NEW.id
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION refresh_product_summary()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY product_summary;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql; 