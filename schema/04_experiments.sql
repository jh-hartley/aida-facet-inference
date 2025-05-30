-- Tables for experiment tracking
CREATE TABLE experiment_runs (
    run_id SERIAL PRIMARY KEY,
    experiment_name TEXT,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status TEXT,
    parameters JSONB
);

CREATE TABLE experiment_metrics (
    metric_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES experiment_runs(run_id),
    metric_name TEXT,
    metric_value FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE experiment_artifacts (
    artifact_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES experiment_runs(run_id),
    artifact_name TEXT,
    artifact_path TEXT,
    artifact_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
); 