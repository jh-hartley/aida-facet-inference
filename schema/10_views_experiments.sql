-- Experiment summary view
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_views WHERE viewname = 'experiment_summary'
    ) THEN
        CREATE VIEW experiment_summary AS
        SELECT 
            pe.experiment_key,
            pe.created_at,
            pe.started_at,
            pe.completed_at,
            pe.total_predictions,
            pe.total_products,
            pe.average_time_per_prediction,
            COUNT(DISTINCT pr.prediction_key) AS prediction_count
        FROM prediction_experiments pe
        LEFT JOIN prediction_results pr ON pe.experiment_key = pr.experiment_key
        GROUP BY pe.experiment_key, pe.created_at, pe.started_at, pe.completed_at, pe.total_predictions, pe.total_products, pe.average_time_per_prediction;
    END IF;
END $$;

-- Metric trends view (example: confidence over time)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_views WHERE viewname = 'metric_trends'
    ) THEN
        CREATE VIEW metric_trends AS
        SELECT 
            pe.experiment_key,
            pr.attribute_key,
            pr.created_at,
            pr.confidence,
            LAG(pr.confidence) OVER (PARTITION BY pe.experiment_key, pr.attribute_key ORDER BY pr.created_at) AS previous_confidence,
            pr.confidence - LAG(pr.confidence) OVER (PARTITION BY pe.experiment_key, pr.attribute_key ORDER BY pr.created_at) AS confidence_change
        FROM prediction_experiments pe
        JOIN prediction_results pr ON pe.experiment_key = pr.experiment_key
        ORDER BY pe.experiment_key, pr.attribute_key, pr.created_at;
    END IF;
END $$; 