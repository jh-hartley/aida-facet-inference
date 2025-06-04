CREATE INDEX IF NOT EXISTS idx_prediction_experiments_created_at ON prediction_experiments(created_at);
CREATE INDEX IF NOT EXISTS idx_prediction_experiments_completed_at ON prediction_experiments(completed_at);
CREATE INDEX IF NOT EXISTS idx_prediction_results_experiment_key ON prediction_results(experiment_key);
CREATE INDEX IF NOT EXISTS idx_prediction_results_product_key ON prediction_results(product_key);
CREATE INDEX IF NOT EXISTS idx_prediction_results_attribute_key ON prediction_results(attribute_key);
CREATE INDEX IF NOT EXISTS idx_prediction_results_recommendation_key ON prediction_results(recommendation_key); 