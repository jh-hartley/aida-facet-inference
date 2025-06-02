from uuid import uuid4

from src.common.db import db_session
from src.csv_ingestion.records import RawRecommendationRecord
from src.csv_ingestion.repositories import RawRecommendationRepository


def create_recommendation(
    product_key: str,
    attribute_key: str,
    value: str,
    confidence: float,
) -> RawRecommendationRecord | None:
    """Create a new recommendation if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawRecommendationRepository(session)

        if (
            repo.find_by_product_key_and_attribute_key_and_value(
                product_key, attribute_key, value
            )
            is not None
        ):
            return None

        recommendation = RawRecommendationRecord(
            recommendation_key=str(uuid4()),
            product_key=product_key,
            attribute_key=attribute_key,
            value=value,
            confidence=confidence,
        )

        return repo.create(recommendation)
