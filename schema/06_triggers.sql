CREATE TRIGGER create_retailer_partitions_trigger
    AFTER INSERT ON retailers
    FOR EACH ROW
    EXECUTE FUNCTION create_retailer_partitions();

CREATE TRIGGER refresh_product_summary_products
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

CREATE TRIGGER refresh_product_summary_retailer_products
    AFTER INSERT OR UPDATE OR DELETE ON retailer_products
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary(); 