CREATE INDEX IF NOT EXISTS idx_raw_products_key ON raw_products(product_key);
CREATE INDEX IF NOT EXISTS idx_raw_categories_key ON raw_categories(category_key);
CREATE INDEX IF NOT EXISTS idx_raw_attributes_key ON raw_attributes(attribute_key);
CREATE INDEX IF NOT EXISTS idx_raw_product_categories ON raw_product_categories(product_key, category_key);
CREATE INDEX IF NOT EXISTS idx_raw_product_attribute_values ON raw_product_attribute_values(product_key, attribute_key);
CREATE INDEX IF NOT EXISTS idx_product_summary_product_key ON product_summary(product_key);
CREATE INDEX IF NOT EXISTS idx_product_summary_category ON product_summary(category_key); 