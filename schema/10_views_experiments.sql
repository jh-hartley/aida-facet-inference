-- Views for experiment tables
-- Experiment summary view
CREATE VIEW IF NOT EXISTS experiment_summary AS
SELECT 
    er.run_id,
    er.experiment_name,
    er.start_time,
    er.end_time,
    er.status,
    COUNT(DISTINCT em.metric_id) AS metric_count,
    COUNT(DISTINCT ea.artifact_id) AS artifact_count,
    MIN(em.metric_value) AS min_metric_value,
    MAX(em.metric_value) AS max_metric_value,
    AVG(em.metric_value) AS avg_metric_value
FROM experiment_runs er
LEFT JOIN experiment_metrics em ON er.run_id = em.run_id
LEFT JOIN experiment_artifacts ea ON er.run_id = ea.run_id
GROUP BY er.run_id, er.experiment_name, er.start_time, er.end_time, er.status;

-- Metric trends view
CREATE VIEW IF NOT EXISTS metric_trends AS
SELECT 
    er.experiment_name,
    em.metric_name,
    em.timestamp,
    em.metric_value,
    LAG(em.metric_value) OVER (PARTITION BY er.experiment_name, em.metric_name ORDER BY em.timestamp) AS previous_value,
    em.metric_value - LAG(em.metric_value) OVER (PARTITION BY er.experiment_name, em.metric_name ORDER BY em.timestamp) AS value_change
FROM experiment_runs er
JOIN experiment_metrics em ON er.run_id = em.run_id
ORDER BY er.experiment_name, em.metric_name, em.timestamp; 