from typing import Any
from src.core.infrastructure.database.input_data.repositories import Repository
from src.core.infrastructure.database.predictions.records import PredictionExperimentRecord, PredictionResultRecord
from sqlalchemy import select
from sqlalchemy.orm import Session


class PredictionResultRepository(Repository[PredictionResultRecord]):
    """Repository for prediction result data"""

    def __init__(self, session: Session):
        super().__init__(session, PredictionResultRecord)

    def get_by_experiment_key(
        self, experiment_key: str
    ) -> list[PredictionResultRecord]:
        result = list(
            self.session.scalars(
                select(PredictionResultRecord).where(
                    PredictionResultRecord.experiment_key == experiment_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No predictions found for experiment {experiment_key}"
            )
        return result

    def find_by_experiment_key(
        self, experiment_key: str
    ) -> list[PredictionResultRecord]:
        return list(
            self.session.scalars(
                select(PredictionResultRecord).where(
                    PredictionResultRecord.experiment_key == experiment_key
                )
            ).all()
        )

    def get_by_product_key(
        self, product_key: str
    ) -> list[PredictionResultRecord]:
        result = list(
            self.session.scalars(
                select(PredictionResultRecord).where(
                    PredictionResultRecord.product_key == product_key
                )
            ).all()
        )
        if not result:
            raise ValueError(f"No predictions found for product {product_key}")
        return result

    def find_by_product_key(
        self, product_key: str
    ) -> list[PredictionResultRecord]:
        return list(
            self.session.scalars(
                select(PredictionResultRecord).where(
                    PredictionResultRecord.product_key == product_key
                )
            ).all()
        )

    def find_by_recommendation_key(
        self, recommendation_key: str
    ) -> list[PredictionResultRecord]:
        return list(
            self.session.scalars(
                select(PredictionResultRecord).where(
                    PredictionResultRecord.recommendation_key
                    == recommendation_key
                )
            ).all()
        )

    def get_by_confidence_range(
        self,
        min_confidence: float,
        max_confidence: float,
        experiment_key: str | None = None,
    ) -> list[PredictionResultRecord]:
        """
        Get predictions within a confidence range,
        optionally for a specific experiment.
        """
        query = select(PredictionResultRecord).where(
            PredictionResultRecord.confidence >= min_confidence,
            PredictionResultRecord.confidence <= max_confidence,
        )
        if experiment_key:
            query = query.where(
                PredictionResultRecord.experiment_key == experiment_key
            )
        return list(self.session.scalars(query).all())

    def get_by_attribute_key(
        self, attribute_key: str, experiment_key: str | None = None
    ) -> list[PredictionResultRecord]:
        """
        Get predictions for a specific attribute,
        optionally for a specific experiment.
        """
        query = select(PredictionResultRecord).where(
            PredictionResultRecord.attribute_key == attribute_key
        )
        if experiment_key:
            query = query.where(
                PredictionResultRecord.experiment_key == experiment_key
            )
        return list(self.session.scalars(query).all())

    def get_latest_predictions(
        self, limit: int = 10
    ) -> list[PredictionResultRecord]:
        """Get the most recent predictions."""
        return list(
            self.session.scalars(
                select(PredictionResultRecord)
                .order_by(PredictionResultRecord.created_at.desc())
                .limit(limit)
            ).all()
        )


class PredictionExperimentRepository(Repository[PredictionExperimentRecord]):
    """Repository for prediction experiment data"""

    def __init__(self, session: Session):
        super().__init__(session, PredictionExperimentRecord)

    def get_by_experiment_key(
        self, experiment_key: str
    ) -> PredictionExperimentRecord:
        result = self.session.get(self.model, experiment_key)
        if result is None:
            raise ValueError(f"No experiment found with key {experiment_key}")
        return result

    def find_by_experiment_key(
        self, experiment_key: str
    ) -> PredictionExperimentRecord | None:
        return self.session.get(self.model, experiment_key)

    def find_all(self) -> list[PredictionExperimentRecord]:
        """Get all experiments, ordered by creation date descending."""
        return list(
            self.session.scalars(
                select(self.model).order_by(self.model.created_at.desc())
            ).all()
        )

    def get_recent_experiments(
        self, limit: int = 10
    ) -> list[PredictionExperimentRecord]:
        """Get the most recent experiments."""
        return list(
            self.session.scalars(
                select(self.model)
                .order_by(self.model.created_at.desc())
                .limit(limit)
            ).all()
        )

    def get_completed_experiments(
        self, limit: int = 10
    ) -> list[PredictionExperimentRecord]:
        """Get the most recently completed experiments."""
        return list(
            self.session.scalars(
                select(self.model)
                .where(self.model.completed_at.is_not(None))
                .order_by(self.model.completed_at.desc())
                .limit(limit)
            ).all()
        )

    def get_running_experiments(
        self,
    ) -> list[PredictionExperimentRecord]:
        """Get all experiments that have started but not completed."""
        return list(
            self.session.scalars(
                select(self.model)
                .where(self.model.completed_at.is_(None))
                .order_by(self.model.started_at.desc())
            ).all()
        )

    def get_experiments_by_metadata(
        self, key: str, value: Any
    ) -> list[PredictionExperimentRecord]:
        """Get experiments with matching metadata key-value pair."""
        return list(
            self.session.scalars(
                select(self.model).where(
                    self.model.experiment_metadata[key].astext == str(value)
                )
            ).all()
        )