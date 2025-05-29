CREATE TRIGGER refresh_product_summary_raw_products
    AFTER INSERT OR UPDATE OR DELETE ON raw_products
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

CREATE TRIGGER refresh_product_summary_raw_product_categories
    AFTER INSERT OR UPDATE OR DELETE ON raw_product_categories
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

CREATE TRIGGER refresh_product_summary_raw_product_attribute_values
    AFTER INSERT OR UPDATE OR DELETE ON raw_product_attribute_values
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary(); 