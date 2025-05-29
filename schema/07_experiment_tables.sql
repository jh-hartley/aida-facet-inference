CREATE TABLE prediction_experiments (
    experiment_key TEXT PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE TABLE prediction_results (
    prediction_key TEXT PRIMARY KEY,
    experiment_key TEXT REFERENCES prediction_experiments(experiment_key),
    product_key TEXT, -- REFERENCES raw_products(product_key)
    attribute_key TEXT, -- REFERENCES raw_attributes(attribute_key)
    value TEXT,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    recommendation_key TEXT -- REFERENCES raw_recommendations(recommendation_key)
);
