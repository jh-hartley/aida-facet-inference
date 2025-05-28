-- Raw CSV data ingestion tables
-- These tables store the raw data from CSV files before processing

-- Product data
CREATE TABLE raw_products (
    product_key TEXT PRIMARY KEY,
    system_name TEXT,
    friendly_name TEXT
);

-- Category data
CREATE TABLE raw_categories (
    category_key TEXT PRIMARY KEY,
    system_name TEXT,
    friendly_name TEXT
);

-- Attribute data
CREATE TABLE raw_attributes (
    attribute_key TEXT PRIMARY KEY,
    system_name TEXT,
    friendly_name TEXT,
    attribute_type TEXT,
    unit_measure_type TEXT
);

-- Product-Category relationships
CREATE TABLE raw_product_categories (
    product_key TEXT REFERENCES raw_products(product_key),
    category_key TEXT REFERENCES raw_categories(category_key),
    PRIMARY KEY (product_key, category_key)
);

-- Category-Attribute relationships
CREATE TABLE raw_category_attributes (
    category_key TEXT REFERENCES raw_categories(category_key),
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    PRIMARY KEY (category_key, attribute_key)
);

-- Product Attribute Values
CREATE TABLE raw_product_attribute_values (
    product_key TEXT REFERENCES raw_products(product_key),
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    value TEXT,
    PRIMARY KEY (product_key, attribute_key)
);

-- Product Attribute Gaps
CREATE TABLE raw_product_attribute_gaps (
    product_key TEXT REFERENCES raw_products(product_key),
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    PRIMARY KEY (product_key, attribute_key)
);

-- Product Attribute Allowable Values
CREATE TABLE raw_product_attribute_allowable_values (
    product_key TEXT REFERENCES raw_products(product_key),
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    value TEXT,
    PRIMARY KEY (product_key, attribute_key, value)
);

-- Category Allowable Values
CREATE TABLE raw_category_allowable_values (
    category_key TEXT REFERENCES raw_categories(category_key),
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    value TEXT,
    PRIMARY KEY (category_key, attribute_key, value)
);

-- Attribute Allowable Values Applicable in Every Category
CREATE TABLE raw_attribute_allowable_values_applicable_in_every_category (
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    value TEXT,
    PRIMARY KEY (attribute_key, value)
);

-- Attribute Allowable Values in Any Category
CREATE TABLE raw_attribute_allowable_values_in_any_category (
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    value TEXT,
    PRIMARY KEY (attribute_key, value)
);

-- Recommendation data
CREATE TABLE raw_recommendations (
    recommendation_key TEXT PRIMARY KEY,
    product_key TEXT REFERENCES raw_products(product_key),
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    value TEXT,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Recommendation Round data
CREATE TABLE raw_recommendation_rounds (
    round_key TEXT PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Rich Text Source data
CREATE TABLE raw_rich_text_sources (
    source_key TEXT PRIMARY KEY,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
); 