from datetime import datetime, timezone
from typing import cast

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, exists, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.common.clock import clock
from src.common.db import Base
from src.core.infrastructure.database.embeddings.models import ProductEmbedding


class ProductEmbeddingRecord(Base):
    """SQLAlchemy record for product embeddings"""

    __tablename__ = "product_embeddings"

    product_key: Mapped[str] = mapped_column(String, primary_key=True)
    product_description: Mapped[str] = mapped_column(String)
    embedding: Mapped[Vector] = mapped_column(Vector(1536))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def to_dto(self) -> ProductEmbedding:
        """Convert to DTO"""
        return ProductEmbedding(
            product_key=self.product_key,
            product_description=self.product_description,
            embedding=cast(list[float], self.embedding),
            created_at=self.created_at.replace(tzinfo=timezone.utc),
            updated_at=self.updated_at.replace(tzinfo=timezone.utc),
        )

    @classmethod
    def from_dto(cls, dto: ProductEmbedding) -> "ProductEmbeddingRecord":
        """Create from DTO"""
        return cls(
            product_key=dto.product_key,
            product_description=dto.product_description,
            embedding=dto.embedding,
            created_at=dto.created_at,
        )


class ProductEmbeddingRepository:
    """Repository for managing product embeddings"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, embedding: ProductEmbedding) -> ProductEmbedding:
        """Create a new product embedding"""
        if not embedding.created_at:
            embedding.created_at = clock.now()
        db_entity = ProductEmbeddingRecord.from_dto(embedding)
        self.session.add(db_entity)
        return embedding

    def update(self, embedding: ProductEmbedding) -> ProductEmbedding:
        """Update an existing product embedding"""
        stmt = (
            update(ProductEmbeddingRecord)
            .where(ProductEmbeddingRecord.product_key == embedding.product_key)
            .values(
                embedding=embedding.embedding, created_at=embedding.created_at
            )
        )
        self.session.execute(stmt)
        return embedding

    def find(self, product_key: str) -> ProductEmbedding | None:
        """Find a product embedding by product key"""
        stmt = select(ProductEmbeddingRecord).where(
            ProductEmbeddingRecord.product_key == product_key
        )
        record = self.session.execute(stmt).scalar()
        if not record:
            return None
        return record.to_dto()

    def exists(self, product_key: str) -> bool:
        """Check if a product embedding exists"""
        stmt = (
            exists()
            .where(ProductEmbeddingRecord.product_key == product_key)
            .select()
        )
        return bool(self.session.execute(stmt).scalar())

    def find_similar_products(
        self,
        embedding: list[float],
        limit: int = 10,
        distance_threshold: float = 0.3,
    ) -> list[tuple[str, float]]:
        """Find similar products using cosine distance"""
        stmt = (
            select(
                ProductEmbeddingRecord.product_key,
                ProductEmbeddingRecord.embedding.cosine_distance(
                    embedding
                ).label("distance"),
            )
            .where(
                ProductEmbeddingRecord.embedding.cosine_distance(embedding)
                <= distance_threshold
            )
            .order_by("distance")
            .limit(limit)
        )

        result = self.session.execute(stmt)
        return [(row.product_key, float(row.distance)) for row in result]
