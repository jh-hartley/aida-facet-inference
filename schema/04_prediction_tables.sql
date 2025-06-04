CREATE TABLE prediction_experiments (
    experiment_key TEXT PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    experiment_metadata JSONB,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    total_predictions INTEGER NOT NULL DEFAULT 0,
    total_products INTEGER NOT NULL DEFAULT 0,
    average_time_per_prediction FLOAT
);

CREATE TABLE prediction_results (
    prediction_key TEXT PRIMARY KEY,
    experiment_key TEXT REFERENCES prediction_experiments(experiment_key),
    product_key TEXT REFERENCES raw_products(product_key),
    attribute_key TEXT REFERENCES raw_attributes(attribute_key),
    value TEXT,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    recommendation_key INTEGER REFERENCES human_recommendations(id),
    unit TEXT,
    actual_value TEXT,
    correctness_status BOOLEAN,
    reasoning TEXT,
    suggested_value TEXT
);