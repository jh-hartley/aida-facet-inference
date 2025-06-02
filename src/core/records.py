from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.connection import Base


class PredictionExperimentRecord(Base):
    """Model for prediction experiment data"""

    __tablename__ = "prediction_experiments"

    experiment_key: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    experiment_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    total_predictions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_products: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    average_time_per_prediction: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )


class PredictionResultRecord(Base):
    """Model for prediction result data"""

    __tablename__ = "prediction_results"

    prediction_key: Mapped[str] = mapped_column(String, primary_key=True)
    experiment_key: Mapped[str] = mapped_column(
        String, ForeignKey("prediction_experiments.experiment_key")
    )
    product_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_products.product_key")
    )
    attribute_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_attributes.attribute_key")
    )
    value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    recommendation_key: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
