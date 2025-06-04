import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_duplicates(csv_path: str) -> None:
    """Check for duplicate product_key and attribute_key pairs in the CSV file."""
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Count total rows
    total_rows = len(df)
    
    # Count unique product_key and attribute_key pairs
    unique_pairs = df[['product_key', 'attribute_key']].drop_duplicates()
    unique_count = len(unique_pairs)
    
    # Find duplicates
    duplicates = df[df.duplicated(['product_key', 'attribute_key'], keep=False)]
    
    logger.info(f"Total rows in file: {total_rows}")
    logger.info(f"Unique product_key + attribute_key pairs: {unique_count}")
    logger.info(f"Number of duplicate pairs: {total_rows - unique_count}")
    
    if len(duplicates) > 0:
        logger.info("\nDuplicate entries found:")
        for _, group in duplicates.groupby(['product_key', 'attribute_key']):
            logger.info(f"\nProduct: {group['product_key'].iloc[0]}")
            logger.info(f"Attribute: {group['attribute_key'].iloc[0]}")
            logger.info(f"Number of duplicates: {len(group)}")
            logger.info("Values:")
            for _, row in group.iterrows():
                logger.info(f"  - predicted_value: {row['predicted_value']}")
                logger.info(f"    actual_value: {row['actual_value']}")

if __name__ == "__main__":
    csv_path = "/Users/jameshartley/Desktop/aida/prediction_results.csv"
    check_duplicates(csv_path) 