import pandas as pd
from difflib import SequenceMatcher
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from src.core.infrastructure.database.input_data.records import HumanRecommendationRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fuzzy_match(predicted: str, ground_truth: str, threshold: float = 0.9) -> bool:
    """Check if predicted value matches ground truth using fuzzy matching."""
    # Normalize strings
    predicted = str(predicted).lower().strip()
    ground_truth = str(ground_truth).lower().strip()

    # Check for exact match first
    if predicted == ground_truth:
        return True

    # Calculate similarity ratio
    similarity = SequenceMatcher(None, predicted, ground_truth).ratio()
    return similarity >= threshold

def get_ground_truth_value(recommendation: HumanRecommendationRecord) -> str:
    """Get the ground truth value based on the recommendation action."""
    if recommendation.action == "Action":
        return ""
    elif recommendation.action == "Make no change":
        return ""
    elif recommendation.action == "Apply override":
        return recommendation.override
    elif recommendation.action == "Accept Recommendation":
        return recommendation.recommendation
    else:
        logger.warning(f"Unknown action type: {recommendation.action}")
        return ""

def process_predictions(csv_path: str, db_url: str) -> None:
    """Process predictions from CSV and calculate accuracy metrics."""
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Connect to database
    engine = create_engine(db_url)
    session = Session(engine)
    
    # Get all recommendations
    recommendations = session.scalars(select(HumanRecommendationRecord)).all()
    
    # Count action types
    action_counts = {
        "Action": 0,
        "Make no change": 0,
        "Apply override": 0,
        "Accept Recommendation": 0
    }
    
    # Process each recommendation
    for rec in recommendations:
        action_counts[rec.action] += 1
        
        # Find matching prediction
        matching_pred = df[
            (df['product_key'] == rec.product_reference) & 
            (df['attribute_key'] == rec.attribute_reference)
        ]
        
        if not matching_pred.empty:
            ground_truth = get_ground_truth_value(rec)
            if ground_truth is not None:  # Skip if action type is "Action"
                df.loc[matching_pred.index, 'actual_value'] = ground_truth
                df.loc[matching_pred.index, 'correctness_status'] = df.loc[matching_pred.index].apply(
                    lambda row: fuzzy_match(row['predicted_value'], ground_truth),
                    axis=1
                )
    
    # Log action type counts
    logger.info("\nAction type counts:")
    for action, count in action_counts.items():
        logger.info(f"{action}: {count}")
    
    # Save the updated CSV
    df.to_csv(csv_path, index=False)
    logger.info(f"\nUpdated CSV file with correctness status at {csv_path}")
    
    # Calculate accuracy per experiment
    for experiment in df['experiment_key'].unique():
        experiment_df = df[df['experiment_key'] == experiment]
        total = len(experiment_df)
        correct = experiment_df['correctness_status'].sum()
        accuracy = correct / total if total > 0 else 0
        
        logger.info(f"\nExperiment: {experiment}")
        logger.info(f"Total predictions: {total}")
        logger.info(f"Correct predictions: {correct}")
        logger.info(f"Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    csv_path = "/Users/jameshartley/Desktop/aida/prediction_results.csv"
    db_url = "postgresql://postgres:postgres@localhost:5432/aida"  # Update this with your actual DB URL
    process_predictions(csv_path, db_url) 