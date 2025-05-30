-- Foreign key indexes
CREATE INDEX IF NOT EXISTS idx_experiment_metrics_run_id ON experiment_metrics(run_id);
CREATE INDEX IF NOT EXISTS idx_experiment_artifacts_run_id ON experiment_artifacts(run_id);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_experiment_runs_name ON experiment_runs(experiment_name);
CREATE INDEX IF NOT EXISTS idx_experiment_runs_status ON experiment_runs(status);
CREATE INDEX IF NOT EXISTS idx_experiment_runs_start_time ON experiment_runs(start_time);

CREATE INDEX IF NOT EXISTS idx_experiment_metrics_name ON experiment_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_experiment_metrics_timestamp ON experiment_metrics(timestamp);

CREATE INDEX IF NOT EXISTS idx_experiment_artifacts_name ON experiment_artifacts(artifact_name);
CREATE INDEX IF NOT EXISTS idx_experiment_artifacts_type ON experiment_artifacts(artifact_type); 