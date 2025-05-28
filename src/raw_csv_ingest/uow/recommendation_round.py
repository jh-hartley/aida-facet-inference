from src.db.connection import db_session
from src.raw_csv_ingest.models import RawRecommendationRound
from src.raw_csv_ingest.repositories import RawRecommendationRoundRepository


def create_recommendation_round(
    round_number: int,
    description: str,
) -> RawRecommendationRound | None:
    """Create a new recommendation round if it doesn't already exist"""
    with db_session().begin() as session:
        repo = RawRecommendationRoundRepository(session)
        
        # Check if round already exists
        if repo.find_by_round_number(round_number):
            return None

        recommendation_round = RawRecommendationRound(
            round_number=round_number,
            description=description,
        )

        return repo.create(recommendation_round) 