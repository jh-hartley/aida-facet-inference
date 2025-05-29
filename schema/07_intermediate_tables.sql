CREATE TABLE raw_products (
    product_key TEXT PRIMARY KEY,
    system_name TEXT,
    friendly_name TEXT
);

CREATE TABLE raw_categories (
    category_key TEXT PRIMARY KEY,
    system_name TEXT,
    friendly_name TEXT
);

CREATE TABLE raw_attributes (
    attribute_key TEXT PRIMARY KEY,
    system_name TEXT,
    friendly_name TEXT,
    attribute_type TEXT,
    unit_measure_type TEXT
);

CREATE TABLE raw_product_categories (
    product_key TEXT, -- REFERENCES raw_products(product_key)
    category_key TEXT, -- REFERENCES raw_categories(category_key)
    PRIMARY KEY (product_key, category_key)
);

-- Category-Attribute relationships
CREATE TABLE raw_category_attributes (
    category_attribute_key TEXT PRIMARY KEY,
    category_key TEXT, -- REFERENCES raw_categories(category_key)
    attribute_key TEXT -- REFERENCES raw_attributes(attribute_key)
);

-- Product Attribute Values
CREATE TABLE raw_product_attribute_values (
    product_key TEXT, -- REFERENCES raw_products(product_key)
    attribute_key TEXT, -- REFERENCES raw_attributes(attribute_key)
    value TEXT,
    PRIMARY KEY (product_key, attribute_key)
);

CREATE TABLE raw_product_attribute_gaps (
    product_key TEXT, -- REFERENCES raw_products(product_key)
    attribute_key TEXT, -- REFERENCES raw_attributes(attribute_key)
    PRIMARY KEY (product_key, attribute_key)
);

CREATE TABLE raw_product_attribute_allowable_values (
    product_key TEXT, -- REFERENCES raw_products(product_key)
    attribute_key TEXT, -- REFERENCES raw_attributes(attribute_key)
    value TEXT,
    PRIMARY KEY (product_key, attribute_key, value)
);

CREATE TABLE raw_category_allowable_values (
    category_key TEXT, -- REFERENCES raw_categories(category_key)
    attribute_key TEXT, -- REFERENCES raw_attributes(attribute_key)
    value TEXT,
    unit_type TEXT,
    minimum_value FLOAT,
    minimum_unit TEXT,
    maximum_value FLOAT,
    maximum_unit TEXT,
    range_qualifier TEXT,
    PRIMARY KEY (category_key, attribute_key, value)
);

CREATE TABLE raw_attribute_allowable_values_applicable_in_every_category (
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    value TEXT,
    PRIMARY KEY (attribute_key, value)
);

CREATE TABLE raw_attribute_allowable_values_in_any_category (
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    value TEXT,
    PRIMARY KEY (attribute_key, value)
);

CREATE TABLE raw_recommendations (
    recommendation_key TEXT PRIMARY KEY,
    product_key TEXT, -- REFERENCES raw_products(product_key)
    attribute_key TEXT, -- REFERENCES raw_attributes(attribute_key)
    value TEXT,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw_recommendation_rounds (
    round_key TEXT PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw_rich_text_sources (
    source_key TEXT PRIMARY KEY,
    product_key TEXT,
    content TEXT,
    name TEXT,
    priority INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
); 