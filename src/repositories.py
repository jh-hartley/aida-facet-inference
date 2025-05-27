from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, Text)
from sqlalchemy.orm import relationship

from src.config import config
from src.db.connection import Base


class RetailerDB(Base):
    """Database model for retailers"""

    __tablename__ = "retailers"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    country = Column(Text, nullable=True)
    industry = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    products = relationship("RetailerProductDB", back_populates="retailer")
    facets = relationship("RetailerFacetDB", back_populates="retailer")
    mappings = relationship("AttributeMappingDB", back_populates="retailer")


class ProductDB(Base):
    """Database model for products"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    identifier_value = Column(Text, nullable=False)
    identifier_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Text, nullable=True)
    attributes = Column(JSON, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    retailers = relationship("RetailerProductDB", back_populates="product")
    embedding = relationship(
        "ProductEmbeddingDB", back_populates="product", uselist=False
    )


class ProductEmbeddingDB(Base):
    """Database model for product embeddings"""

    __tablename__ = "product_embeddings"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    embedding_model = Column(Text, nullable=False)
    embedding = Column(  # type: ignore
        Vector(config.EMBEDDING_DEFAULT_DIMENSIONS), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    product = relationship("ProductDB", back_populates="embedding")


class RetailerFacetDB(Base):
    """Database model for retailer facets"""

    __tablename__ = "retailer_facets"

    id = Column(Integer, primary_key=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    retailer = relationship("RetailerDB", back_populates="facets")


class RetailerProductDB(Base):
    """Database model for retailer products"""

    __tablename__ = "retailer_products"

    id = Column(Integer, primary_key=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    retailer_product_id = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    availability = Column(Boolean, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    retailer = relationship("RetailerDB", back_populates="products")
    product = relationship("ProductDB", back_populates="retailers")
    attributes = relationship(
        "RetailerProductAttributeDB", back_populates="retailer_product"
    )


class RetailerProductAttributeDB(Base):
    """Database model for retailer product attributes"""

    __tablename__ = "retailer_product_attributes"

    retailer_id = Column(Integer, ForeignKey("retailers.id"), primary_key=True)
    retailer_product_id = Column(
        Integer, ForeignKey("retailer_products.id"), primary_key=True
    )
    attribute_name = Column(Text, primary_key=True)
    attribute_value = Column(Text, nullable=False)
    attribute_type = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    retailer_product = relationship(
        "RetailerProductDB", back_populates="attributes"
    )


class AttributeMappingDB(Base):
    """Database model for attribute mappings"""

    __tablename__ = "attribute_mappings"

    id = Column(Integer, primary_key=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    source_attribute = Column(Text, nullable=False)
    normalized_attribute = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    retailer = relationship("RetailerDB", back_populates="mappings")
