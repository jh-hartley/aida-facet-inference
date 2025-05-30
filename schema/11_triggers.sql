-- Function to refresh product summary view
CREATE OR REPLACE FUNCTION refresh_product_summary()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY product_summary;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to refresh product details view
CREATE OR REPLACE FUNCTION refresh_product_details()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY product_details;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to refresh product gaps view
CREATE OR REPLACE FUNCTION refresh_product_gaps()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY product_gaps;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Triggers to refresh product summary view
CREATE TRIGGER refresh_product_summary_products
    AFTER INSERT OR UPDATE OR DELETE ON raw_products
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

CREATE TRIGGER refresh_product_summary_categories
    AFTER INSERT OR UPDATE OR DELETE ON raw_categories
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

CREATE TRIGGER refresh_product_summary_attributes
    AFTER INSERT OR UPDATE OR DELETE ON raw_attributes
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

CREATE TRIGGER refresh_product_summary_product_categories
    AFTER INSERT OR UPDATE OR DELETE ON raw_product_categories
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

CREATE TRIGGER refresh_product_summary_category_attributes
    AFTER INSERT OR UPDATE OR DELETE ON raw_category_attributes
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

CREATE TRIGGER refresh_product_summary_product_attribute_values
    AFTER INSERT OR UPDATE OR DELETE ON raw_product_attribute_values
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

CREATE TRIGGER refresh_product_summary_recommendations
    AFTER INSERT OR UPDATE OR DELETE ON raw_recommendations
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_summary();

-- Triggers to refresh product details view
CREATE TRIGGER refresh_product_details_products
    AFTER INSERT OR UPDATE OR DELETE ON raw_products
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_details();

CREATE TRIGGER refresh_product_details_categories
    AFTER INSERT OR UPDATE OR DELETE ON raw_categories
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_details();

CREATE TRIGGER refresh_product_details_product_categories
    AFTER INSERT OR UPDATE OR DELETE ON raw_product_categories
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_details();

CREATE TRIGGER refresh_product_details_product_attribute_values
    AFTER INSERT OR UPDATE OR DELETE ON raw_product_attribute_values
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_details();

CREATE TRIGGER refresh_product_details_rich_text
    AFTER INSERT OR UPDATE OR DELETE ON raw_rich_text_sources
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_details();

-- Triggers to refresh product gaps view
CREATE TRIGGER refresh_product_gaps_products
    AFTER INSERT OR UPDATE OR DELETE ON raw_products
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_gaps();

CREATE TRIGGER refresh_product_gaps_attributes
    AFTER INSERT OR UPDATE OR DELETE ON raw_attributes
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_gaps();

CREATE TRIGGER refresh_product_gaps_product_attribute_gaps
    AFTER INSERT OR UPDATE OR DELETE ON raw_product_attribute_gaps
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_gaps();

CREATE TRIGGER refresh_product_gaps_category_allowable_values
    AFTER INSERT OR UPDATE OR DELETE ON raw_category_allowable_values
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_gaps();

CREATE TRIGGER refresh_product_gaps_global_allowable_values
    AFTER INSERT OR UPDATE OR DELETE ON raw_attribute_allowable_values_applicable_in_every_category
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_gaps();

CREATE TRIGGER refresh_product_gaps_any_category_allowable_values
    AFTER INSERT OR UPDATE OR DELETE ON raw_attribute_allowable_values_in_any_category
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_product_gaps(); 