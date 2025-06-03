from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.db import Base


class ExperimentRecord(Base):
    """Record for an experiment run."""

    __tablename__ = "prediction_experiments"

    experiment_key: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    experiment_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_predictions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_products: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_time_per_prediction: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    predictions: Mapped[list["PredictionResultRecord"]] = relationship(
        "PredictionResultRecord", back_populates="experiment"
    )


class PredictionResultRecord(Base):
    """Record for a prediction result."""

    __tablename__ = "prediction_results"

    prediction_key: Mapped[str] = mapped_column(String, primary_key=True)
    experiment_key: Mapped[str] = mapped_column(String, ForeignKey("prediction_experiments.experiment_key"))
    product_key: Mapped[str] = mapped_column(String, ForeignKey("raw_products.product_key"))
    attribute_key: Mapped[str] = mapped_column(String, ForeignKey("raw_attributes.attribute_key"))
    value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    recommendation_key: Mapped[int | None] = mapped_column(Integer, ForeignKey("human_recommendations.id"), nullable=True)
    actual_value: Mapped[str] = mapped_column(Text, nullable=True)
    correctness_status: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    experiment: Mapped["ExperimentRecord"] = relationship("ExperimentRecord", back_populates="predictions")
