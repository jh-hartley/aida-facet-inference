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

        if (
            repo.find_by_product_key_and_attribute_key_and_value(
                product_key, attribute_key, value
            )
            is not None
        ):
            return None

        recommendation = RawRecommendation(
            product_key=product_key,
            attribute_key=attribute_key,
            value=value,
            confidence=confidence,
        )

        return repo.create(recommendation)
