from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.connection import Base


class PredictionExperimentRecord(Base):
    """Record for prediction experiments."""

    __tablename__ = "prediction_experiments"

    experiment_key: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)


class PredictionResultRecord(Base):
    """Record for prediction results."""

    __tablename__ = "prediction_results"

    prediction_key: Mapped[str] = mapped_column(String, primary_key=True)
    experiment_key: Mapped[str] = mapped_column(
        String, ForeignKey("prediction_experiments.experiment_key")
    )
    product_key: Mapped[str] = mapped_column(String)
    attribute_key: Mapped[str] = mapped_column(String)
    value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    recommendation_key: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
