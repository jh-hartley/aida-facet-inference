from src.db.connection import db_session
from src.raw_csv_ingest.models import RawRecommendation
from src.raw_csv_ingest.repositories import RawRecommendationRepository


def create_recommendation(
    product_key: str,
    attribute_key: str,
    value: str,
    confidence: float,
) -> RawRecommendation | None:
    """Create a new recommendation if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawRecommendationRepository(session)
        
        # Check if recommendation already exists
        existing = repo.find_by_product_key(product_key)
        if any(r.attribute_key == attribute_key and r.value == value for r in existing):
            return None

        recommendation = RawRecommendation(
            product_key=product_key,
            attribute_key=attribute_key,
            value=value,
            confidence=confidence,
        )

        return repo.create(recommendation) 