from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.connection import Base


class RawProductRecord(Base):
    """Model for raw product data from CSV"""

    __tablename__ = "raw_products"

    product_key: Mapped[str] = mapped_column(String, primary_key=True)
    system_name: Mapped[str] = mapped_column(String)
    friendly_name: Mapped[str] = mapped_column(String)


class RawCategoryRecord(Base):
    """Model for raw category data from CSV"""

    __tablename__ = "raw_categories"

    category_key: Mapped[str] = mapped_column(String, primary_key=True)
    system_name: Mapped[str] = mapped_column(String)
    friendly_name: Mapped[str] = mapped_column(String)


class RawAttributeRecord(Base):
    """Model for raw attribute data from CSV"""

    __tablename__ = "raw_attributes"

    attribute_key: Mapped[str] = mapped_column(String, primary_key=True)
    system_name: Mapped[str] = mapped_column(String)
    friendly_name: Mapped[str] = mapped_column(String)
    attribute_type: Mapped[str] = mapped_column(String)
    unit_measure_type: Mapped[str] = mapped_column(String)


class RawProductCategoryRecord(Base):
    """Model for raw product-category relationship data from CSV"""

    __tablename__ = "raw_product_categories"

    product_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_products.product_key"), primary_key=True
    )
    category_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_categories.category_key"), primary_key=True
    )


class RawCategoryAttributeRecord(Base):
    """Model for raw category-attribute relationship data from CSV"""

    __tablename__ = "raw_category_attributes"

    category_attribute_key: Mapped[str] = mapped_column(
        String, primary_key=True
    )
    category_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_categories.category_key")
    )
    attribute_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_attributes.attribute_key")
    )


class RawProductAttributeValueRecord(Base):
    """Model for raw product attribute value data from CSV"""

    __tablename__ = "raw_product_attribute_values"

    product_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_products.product_key"), primary_key=True
    )
    attribute_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_attributes.attribute_key"), primary_key=True
    )
    value: Mapped[str] = mapped_column(Text)


class RawProductAttributeGapRecord(Base):
    """Model for raw product attribute gap data from CSV"""

    __tablename__ = "raw_product_attribute_gaps"

    product_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_products.product_key"), primary_key=True
    )
    attribute_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_attributes.attribute_key"), primary_key=True
    )


class RawProductAttributeAllowableValueRecord(Base):
    """Model for raw product attribute allowable value data from CSV"""

    __tablename__ = "raw_product_attribute_allowable_values"

    product_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_products.product_key"), primary_key=True
    )
    attribute_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_attributes.attribute_key"), primary_key=True
    )
    value: Mapped[str] = mapped_column(Text, primary_key=True)


class RawCategoryAllowableValueRecord(Base):
    """Model for raw category allowable value data from CSV"""

    __tablename__ = "raw_category_allowable_values"

    category_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_categories.category_key"), primary_key=True
    )
    attribute_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_attributes.attribute_key"), primary_key=True
    )
    value: Mapped[str] = mapped_column(Text, primary_key=True)
    unit_type: Mapped[str | None] = mapped_column(String, nullable=True)
    minimum_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    minimum_unit: Mapped[str | None] = mapped_column(String, nullable=True)
    maximum_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    maximum_unit: Mapped[str | None] = mapped_column(String, nullable=True)
    range_qualifier: Mapped[str | None] = mapped_column(String, nullable=True)


class RawRecommendationRecord(Base):
    """Model for raw recommendation data from CSV"""

    __tablename__ = "raw_recommendations"

    recommendation_key: Mapped[str] = mapped_column(String, primary_key=True)
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
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class RawRichTextSourceRecord(Base):
    """Model for raw rich text source data from CSV"""

    __tablename__ = "raw_rich_text_sources"

    source_key: Mapped[str] = mapped_column(String, primary_key=True)
    product_key: Mapped[str] = mapped_column(
        String, ForeignKey("raw_products.product_key")
    )
    content: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String)
    priority: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
