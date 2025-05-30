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
    product_key TEXT,
    category_key TEXT,
    PRIMARY KEY (product_key, category_key)
);

CREATE TABLE raw_category_attributes (
    category_attribute_key TEXT PRIMARY KEY,
    category_key TEXT,
    attribute_key TEXT
);

CREATE TABLE raw_product_attribute_values (
    product_key TEXT,
    attribute_key TEXT,
    value TEXT,
    PRIMARY KEY (product_key, attribute_key)
);

CREATE TABLE raw_product_attribute_gaps (
    product_key TEXT,
    attribute_key TEXT,
    PRIMARY KEY (product_key, attribute_key)
);

CREATE TABLE raw_category_allowable_values (
    category_key TEXT,
    attribute_key TEXT,
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
    attribute_key TEXT,
    value TEXT,
    PRIMARY KEY (attribute_key, value)
);

CREATE TABLE raw_attribute_allowable_values_in_any_category (
    attribute_key TEXT,
    value TEXT,
    PRIMARY KEY (attribute_key, value)
);

CREATE TABLE raw_recommendations (
    recommendation_key TEXT PRIMARY KEY,
    product_key TEXT,
    attribute_key TEXT,
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

CREATE TABLE human_recommendations (
    id SERIAL PRIMARY KEY,
    product_reference TEXT,
    attribute_reference TEXT,
    attribute_name TEXT,
    recommendation TEXT,
    unit TEXT,
    override TEXT,
    alternative_override TEXT,
    action TEXT,
    link_to_site TEXT,
    comment TEXT
); 