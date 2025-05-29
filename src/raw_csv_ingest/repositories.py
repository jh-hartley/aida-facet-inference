from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.raw_csv_ingest.models import (
    Base,
    RawAttribute,
    RawCategory,
    RawCategoryAllowableValue,
    RawCategoryAttribute,
    RawProduct,
    RawProductAttributeAllowableValue,
    RawProductAttributeGap,
    RawProductAttributeValue,
    RawProductCategory,
    RawRecommendation,
    RawRichTextSource,
)

T = TypeVar("T", bound=Base)


class Repository(Generic[T]):
    """Repository class with common functionality"""

    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model

    def add(self, entity: T) -> None:
        self.session.add(entity)

    def add_all(self, entities: list[T]) -> None:
        self.session.add_all(entities)

    def create(self, entity: T) -> T:
        self.session.add(entity)
        return entity

    def get_by_id(self, id: str) -> T:
        result = self.session.get(self.model, id)
        if result is None:
            raise ValueError(f"No {self.model.__name__} found with id {id}")
        return result

    def find_by_id(self, id: str) -> T | None:
        return self.session.get(self.model, id)

    def get_all(self) -> list[T]:
        return list(self.session.scalars(select(self.model)).all())


class RawProductRepository(Repository[RawProduct]):
    """Repository for raw product data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProduct)

    def get_by_system_name(self, system_name: str) -> RawProduct:
        result = self.session.scalar(
            select(RawProduct).where(RawProduct.system_name == system_name)
        )
        if result is None:
            raise ValueError(
                f"No product found with system name {system_name}"
            )
        return result

    def find_by_system_name(self, system_name: str) -> RawProduct | None:
        return self.session.scalar(
            select(RawProduct).where(RawProduct.system_name == system_name)
        )


class RawCategoryRepository(Repository[RawCategory]):
    """Repository for raw category data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawCategory)

    def get_by_system_name(self, system_name: str) -> RawCategory:
        result = self.session.scalar(
            select(RawCategory).where(RawCategory.system_name == system_name)
        )
        if result is None:
            raise ValueError(
                f"No category found with system name {system_name}"
            )
        return result

    def find_by_system_name(self, system_name: str) -> RawCategory | None:
        return self.session.scalar(
            select(RawCategory).where(RawCategory.system_name == system_name)
        )


class RawAttributeRepository(Repository[RawAttribute]):
    """Repository for raw attribute data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawAttribute)

    def get_by_system_name(self, system_name: str) -> RawAttribute:
        result = self.session.scalar(
            select(RawAttribute).where(RawAttribute.system_name == system_name)
        )
        if result is None:
            raise ValueError(
                f"No attribute found with system name {system_name}"
            )
        return result

    def find_by_system_name(self, system_name: str) -> RawAttribute | None:
        return self.session.scalar(
            select(RawAttribute).where(RawAttribute.system_name == system_name)
        )


class RawProductCategoryRepository(Repository[RawProductCategory]):
    """Repository for raw product-category relationship data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductCategory)

    def get_by_product_key(self, product_key: str) -> list[RawProductCategory]:
        result = list(
            self.session.scalars(
                select(RawProductCategory).where(
                    RawProductCategory.product_key == product_key
                )
            ).all()
        )
        if not result:
            raise ValueError(f"No categories found for product {product_key}")
        return result

    def find_by_product_key(
        self, product_key: str
    ) -> list[RawProductCategory]:
        return list(
            self.session.scalars(
                select(RawProductCategory).where(
                    RawProductCategory.product_key == product_key
                )
            ).all()
        )

    def get_by_category_key(
        self, category_key: str
    ) -> list[RawProductCategory]:
        result = list(
            self.session.scalars(
                select(RawProductCategory).where(
                    RawProductCategory.category_key == category_key
                )
            ).all()
        )
        if not result:
            raise ValueError(f"No products found in category {category_key}")
        return result

    def find_by_category_key(
        self, category_key: str
    ) -> list[RawProductCategory]:
        return list(
            self.session.scalars(
                select(RawProductCategory).where(
                    RawProductCategory.category_key == category_key
                )
            ).all()
        )

    def find_by_product_key_and_category_key(
        self, product_key: str, category_key: str
    ) -> RawProductCategory | None:
        return self.session.scalar(
            select(RawProductCategory).where(
                RawProductCategory.product_key == product_key,
                RawProductCategory.category_key == category_key,
            )
        )


class RawCategoryAttributeRepository(Repository[RawCategoryAttribute]):
    """Repository for raw category-attribute relationship data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawCategoryAttribute)

    def get_by_category_key(
        self, category_key: str
    ) -> list[RawCategoryAttribute]:
        result = list(
            self.session.scalars(
                select(RawCategoryAttribute).where(
                    RawCategoryAttribute.category_key == category_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No attributes found for category {category_key}"
            )
        return result

    def find_by_category_key(
        self, category_key: str
    ) -> list[RawCategoryAttribute]:
        return list(
            self.session.scalars(
                select(RawCategoryAttribute).where(
                    RawCategoryAttribute.category_key == category_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawCategoryAttribute]:
        result = list(
            self.session.scalars(
                select(RawCategoryAttribute).where(
                    RawCategoryAttribute.attribute_key == attribute_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No categories found for attribute {attribute_key}"
            )
        return result

    def find_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawCategoryAttribute]:
        return list(
            self.session.scalars(
                select(RawCategoryAttribute).where(
                    RawCategoryAttribute.attribute_key == attribute_key
                )
            ).all()
        )

    def find_by_category_key_and_attribute_key(
        self, category_key: str, attribute_key: str
    ) -> RawCategoryAttribute | None:
        return self.session.scalar(
            select(RawCategoryAttribute).where(
                RawCategoryAttribute.category_key == category_key,
                RawCategoryAttribute.attribute_key == attribute_key,
            )
        )


class RawProductAttributeValueRepository(Repository[RawProductAttributeValue]):
    """Repository for raw product attribute value data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductAttributeValue)

    def get_by_product_key(
        self, product_key: str
    ) -> list[RawProductAttributeValue]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeValue).where(
                    RawProductAttributeValue.product_key == product_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No attribute values found for product {product_key}"
            )
        return result

    def find_by_product_key(
        self, product_key: str
    ) -> list[RawProductAttributeValue]:
        return list(
            self.session.scalars(
                select(RawProductAttributeValue).where(
                    RawProductAttributeValue.product_key == product_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawProductAttributeValue]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeValue).where(
                    RawProductAttributeValue.attribute_key == attribute_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No product values found for attribute {attribute_key}"
            )
        return result

    def find_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawProductAttributeValue]:
        return list(
            self.session.scalars(
                select(RawProductAttributeValue).where(
                    RawProductAttributeValue.attribute_key == attribute_key
                )
            ).all()
        )

    def find_by_product_key_and_attribute_key_and_value(
        self, product_key: str, attribute_key: str, value: str
    ) -> RawProductAttributeValue | None:
        return self.session.scalar(
            select(RawProductAttributeValue).where(
                RawProductAttributeValue.product_key == product_key,
                RawProductAttributeValue.attribute_key == attribute_key,
                RawProductAttributeValue.value == value,
            )
        )


class RawProductAttributeGapRepository(Repository[RawProductAttributeGap]):
    """Repository for raw product attribute gap data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductAttributeGap)

    def get_by_product_key(
        self, product_key: str
    ) -> list[RawProductAttributeGap]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeGap).where(
                    RawProductAttributeGap.product_key == product_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No attribute gaps found for product {product_key}"
            )
        return result

    def find_by_product_key(
        self, product_key: str
    ) -> list[RawProductAttributeGap]:
        return list(
            self.session.scalars(
                select(RawProductAttributeGap).where(
                    RawProductAttributeGap.product_key == product_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawProductAttributeGap]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeGap).where(
                    RawProductAttributeGap.attribute_key == attribute_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No product gaps found for attribute {attribute_key}"
            )
        return result

    def find_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawProductAttributeGap]:
        return list(
            self.session.scalars(
                select(RawProductAttributeGap).where(
                    RawProductAttributeGap.attribute_key == attribute_key
                )
            ).all()
        )

    def find_by_product_key_and_attribute_key(
        self, product_key: str, attribute_key: str
    ) -> RawProductAttributeGap | None:
        return self.session.scalar(
            select(RawProductAttributeGap).where(
                RawProductAttributeGap.product_key == product_key,
                RawProductAttributeGap.attribute_key == attribute_key,
            )
        )


class RawProductAttributeAllowableValueRepository(
    Repository[RawProductAttributeAllowableValue]
):
    """
    Repository for raw product attribute allowable value data from CSV
    """

    def __init__(self, session: Session):
        super().__init__(session, RawProductAttributeAllowableValue)

    def get_by_product_key(
        self, product_key: str
    ) -> list[RawProductAttributeAllowableValue]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeAllowableValue).where(
                    RawProductAttributeAllowableValue.product_key
                    == product_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No allowable values found for product {product_key}"
            )
        return result

    def find_by_product_key(
        self, product_key: str
    ) -> list[RawProductAttributeAllowableValue]:
        """Find all allowable values for a product"""
        return list(
            self.session.scalars(
                select(RawProductAttributeAllowableValue).where(
                    RawProductAttributeAllowableValue.product_key
                    == product_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawProductAttributeAllowableValue]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeAllowableValue).where(
                    RawProductAttributeAllowableValue.attribute_key
                    == attribute_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No product allowable values found "
                f"for attribute {attribute_key}"
            )
        return result

    def find_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawProductAttributeAllowableValue]:
        """Find all product allowable values for an attribute"""
        return list(
            self.session.scalars(
                select(RawProductAttributeAllowableValue).where(
                    RawProductAttributeAllowableValue.attribute_key
                    == attribute_key
                )
            ).all()
        )

    def find_by_product_key_and_attribute_key_and_value(
        self, product_key: str, attribute_key: str, value: str
    ) -> RawProductAttributeAllowableValue | None:
        return self.session.scalar(
            select(RawProductAttributeAllowableValue).where(
                RawProductAttributeAllowableValue.product_key == product_key,
                RawProductAttributeAllowableValue.attribute_key
                == attribute_key,
                RawProductAttributeAllowableValue.value == value,
            )
        )


class RawCategoryAllowableValueRepository(
    Repository[RawCategoryAllowableValue]
):
    """Repository for raw category allowable value data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawCategoryAllowableValue)

    def get_by_category_key(
        self, category_key: str
    ) -> list[RawCategoryAllowableValue]:
        result = list(
            self.session.scalars(
                select(RawCategoryAllowableValue).where(
                    RawCategoryAllowableValue.category_key == category_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No allowable values found for category {category_key}"
            )
        return result

    def find_by_category_key(
        self, category_key: str
    ) -> list[RawCategoryAllowableValue]:
        return list(
            self.session.scalars(
                select(RawCategoryAllowableValue).where(
                    RawCategoryAllowableValue.category_key == category_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawCategoryAllowableValue]:
        result = list(
            self.session.scalars(
                select(RawCategoryAllowableValue).where(
                    RawCategoryAllowableValue.attribute_key == attribute_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No category allowable values found "
                f"for attribute {attribute_key}"
            )
        return result

    def find_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawCategoryAllowableValue]:
        return list(
            self.session.scalars(
                select(RawCategoryAllowableValue).where(
                    RawCategoryAllowableValue.attribute_key == attribute_key
                )
            ).all()
        )

    def find_by_category_key_and_attribute_key_and_value(
        self, category_key: str, attribute_key: str, value: str
    ) -> RawCategoryAllowableValue | None:
        return self.session.scalar(
            select(RawCategoryAllowableValue).where(
                RawCategoryAllowableValue.category_key == category_key,
                RawCategoryAllowableValue.attribute_key == attribute_key,
                RawCategoryAllowableValue.value == value,
            )
        )


class RawRecommendationRepository(Repository[RawRecommendation]):
    """Repository for raw recommendation data"""

    def __init__(self, session: Session):
        super().__init__(session, RawRecommendation)

    def get_by_product_key(self, product_key: str) -> list[RawRecommendation]:
        result = list(
            self.session.scalars(
                select(RawRecommendation).where(
                    RawRecommendation.product_key == product_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No recommendations found for product {product_key}"
            )
        return result

    def find_by_product_key(self, product_key: str) -> list[RawRecommendation]:
        return list(
            self.session.scalars(
                select(RawRecommendation).where(
                    RawRecommendation.product_key == product_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawRecommendation]:
        result = list(
            self.session.scalars(
                select(RawRecommendation).where(
                    RawRecommendation.attribute_key == attribute_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No recommendations found for attribute {attribute_key}"
            )
        return result

    def find_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawRecommendation]:
        return list(
            self.session.scalars(
                select(RawRecommendation).where(
                    RawRecommendation.attribute_key == attribute_key
                )
            ).all()
        )

    def find_by_product_key_and_attribute_key_and_value(
        self, product_key: str, attribute_key: str, value: str
    ) -> RawRecommendation | None:
        return self.session.scalar(
            select(RawRecommendation).where(
                RawRecommendation.product_key == product_key,
                RawRecommendation.attribute_key == attribute_key,
                RawRecommendation.value == value,
            )
        )


class RawRichTextSourceRepository(Repository[RawRichTextSource]):
    """Repository for raw rich text source data"""

    def __init__(self, session: Session):
        super().__init__(session, RawRichTextSource)

    def find_by_product_key(self, product_key: str) -> list[RawRichTextSource]:
        """Find all rich text sources for a product"""
        return list(
            self.session.scalars(
                select(RawRichTextSource).where(
                    RawRichTextSource.product_key == product_key
                )
            ).all()
        )

    def find_by_product_key_and_name(
        self, product_key: str, name: str
    ) -> RawRichTextSource | None:
        return self.session.scalar(
            select(RawRichTextSource).where(
                RawRichTextSource.product_key == product_key,
                RawRichTextSource.name == name,
            )
        )
