-- Foreign key indexes
CREATE INDEX IF NOT EXISTS idx_product_categories_product_key ON raw_product_categories(product_key);
CREATE INDEX IF NOT EXISTS idx_product_categories_category_key ON raw_product_categories(category_key);

CREATE INDEX IF NOT EXISTS idx_category_attributes_category_key ON raw_category_attributes(category_key);
CREATE INDEX IF NOT EXISTS idx_category_attributes_attribute_key ON raw_category_attributes(attribute_key);

CREATE INDEX IF NOT EXISTS idx_product_attribute_values_product_key ON raw_product_attribute_values(product_key);
CREATE INDEX IF NOT EXISTS idx_product_attribute_values_attribute_key ON raw_product_attribute_values(attribute_key);

CREATE INDEX IF NOT EXISTS idx_product_attribute_gaps_product_key ON raw_product_attribute_gaps(product_key);
CREATE INDEX IF NOT EXISTS idx_product_attribute_gaps_attribute_key ON raw_product_attribute_gaps(attribute_key);

CREATE INDEX IF NOT EXISTS idx_category_allowable_values_category_key ON raw_category_allowable_values(category_key);
CREATE INDEX IF NOT EXISTS idx_category_allowable_values_attribute_key ON raw_category_allowable_values(attribute_key);

CREATE INDEX IF NOT EXISTS idx_recommendations_product_key ON raw_recommendations(product_key);
CREATE INDEX IF NOT EXISTS idx_recommendations_attribute_key ON raw_recommendations(attribute_key);

CREATE INDEX IF NOT EXISTS idx_rich_text_sources_product_key ON raw_rich_text_sources(product_key);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_products_system_name ON raw_products(system_name);
CREATE INDEX IF NOT EXISTS idx_categories_system_name ON raw_categories(system_name);
CREATE INDEX IF NOT EXISTS idx_attributes_system_name ON raw_attributes(system_name);

-- QA table indexes
CREATE INDEX IF NOT EXISTS idx_qa_complete_product_reference ON human_recommendations(product_reference);
CREATE INDEX IF NOT EXISTS idx_qa_complete_attribute_reference ON human_recommendations(attribute_reference); 