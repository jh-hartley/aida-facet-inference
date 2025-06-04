import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def filter_experiment(csv_path: str, experiment_key: str) -> None:
    """Filter CSV file to only include rows with the specified experiment key."""
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Get initial count
    initial_count = len(df)
    
    # Filter for the specific experiment
    filtered_df = df[df['experiment_key'] == experiment_key]
    
    # Get filtered count
    filtered_count = len(filtered_df)
    
    # Save the filtered CSV
    filtered_df.to_csv(csv_path, index=False)
    
    logger.info(f"Original row count: {initial_count}")
    logger.info(f"Filtered row count: {filtered_count}")
    logger.info(f"Removed {initial_count - filtered_count} rows")
    logger.info(f"Updated CSV file at {csv_path}")

if __name__ == "__main__":
    csv_path = "/Users/jameshartley/Desktop/aida/prediction_results.csv"
    experiment_key = "9e7d2e94-6550-43dd-b6bf-812448144bcb"
    filter_experiment(csv_path, experiment_key) 