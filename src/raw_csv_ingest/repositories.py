from typing import TypeVar, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.raw_csv_ingest.models import (
    Base,
    RawProduct,
    RawCategory,
    RawAttribute,
    RawProductCategory,
    RawCategoryAttribute,
    RawProductAttributeValue,
    RawProductAttributeGap,
    RawProductAttributeAllowableValue,
    RawCategoryAllowableValue,
    RawAttributeAllowableValueApplicableInEveryCategory,
    RawAttributeAllowableValueInAnyCategory,
    RawRecommendation,
    RawRecommendationRound,
    RawRichTextSource,
)


T = TypeVar('T', bound=Base, covariant=True)


class Repository:
    """Repository class with common functionality"""

    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model

    def add(self, entity: T) -> None:
        """Add a new entity to the session"""
        self.session.add(entity)

    def add_all(self, entities: list[T]) -> None:
        """Add multiple entities to the session"""
        self.session.add_all(entities)

    def create(self, entity: T) -> T:
        """Create a new entity"""
        self.session.add(entity)
        return entity

    def get_by_id(self, id: str) -> T:
        """Get an entity by its ID, raising an exception if not found"""
        result = self.session.get(self.model, id)
        if result is None:
            raise ValueError(f"No {self.model.__name__} found with id {id}")
        return cast(T, result)

    def find_by_id(self, id: str) -> T | None:
        """Find an entity by its ID, returning None if not found"""
        result = self.session.get(self.model, id)
        return cast(T | None, result)

    def get_all(self) -> list[T]:
        """Get all entities"""
        return cast(list[T], self.session.scalars(select(self.model)).all())


class RawProductRepository(Repository):
    """Repository for raw product data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProduct)

    def create(self, product: RawProduct) -> RawProduct:
        """Create a new product"""
        self.session.add(product)
        return product

    def get_by_system_name(self, system_name: str) -> RawProduct:
        """Get a product by its system name, raising an exception if not found"""
        result = self.session.scalar(
            select(RawProduct).where(RawProduct.system_name == system_name)
        )
        if result is None:
            raise ValueError(f"No product found with system name {system_name}")
        return result

    def find_by_system_name(self, system_name: str) -> RawProduct | None:
        """Find a product by its system name, returning None if not found"""
        return self.session.scalar(
            select(RawProduct).where(RawProduct.system_name == system_name)
        )


class RawCategoryRepository(Repository):
    """Repository for raw category data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawCategory)

    def get_by_system_name(self, system_name: str) -> RawCategory:
        """Get a category by its system name, raising an exception if not found"""
        result = self.session.scalar(
            select(RawCategory).where(RawCategory.system_name == system_name)
        )
        if result is None:
            raise ValueError(f"No category found with system name {system_name}")
        return result

    def find_by_system_name(self, system_name: str) -> RawCategory | None:
        """Find a category by its system name, returning None if not found"""
        return self.session.scalar(
            select(RawCategory).where(RawCategory.system_name == system_name)
        )


class RawAttributeRepository(Repository):
    """Repository for raw attribute data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawAttribute)

    def get_by_system_name(self, system_name: str) -> RawAttribute:
        """Get an attribute by its system name, raising an exception if not found"""
        result = self.session.scalar(
            select(RawAttribute).where(RawAttribute.system_name == system_name)
        )
        if result is None:
            raise ValueError(f"No attribute found with system name {system_name}")
        return result

    def find_by_system_name(self, system_name: str) -> RawAttribute | None:
        """Find an attribute by its system name, returning None if not found"""
        return self.session.scalar(
            select(RawAttribute).where(RawAttribute.system_name == system_name)
        )


class RawProductCategoryRepository(Repository):
    """Repository for raw product-category relationship data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductCategory)

    def get_by_product_key(self, product_key: str) -> list[RawProductCategory]:
        """Get all categories for a product"""
        result = list(
            self.session.scalars(
                select(RawProductCategory).where(RawProductCategory.product_key == product_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No categories found for product {product_key}")
        return result

    def find_by_product_key(self, product_key: str) -> list[RawProductCategory]:
        """Find all categories for a product"""
        return list(
            self.session.scalars(
                select(RawProductCategory).where(RawProductCategory.product_key == product_key)
            ).all()
        )

    def get_by_category_key(self, category_key: str) -> list[RawProductCategory]:
        """Get all products in a category"""
        result = list(
            self.session.scalars(
                select(RawProductCategory).where(RawProductCategory.category_key == category_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No products found in category {category_key}")
        return result

    def find_by_category_key(self, category_key: str) -> list[RawProductCategory]:
        """Find all products in a category"""
        return list(
            self.session.scalars(
                select(RawProductCategory).where(RawProductCategory.category_key == category_key)
            ).all()
        )


class RawCategoryAttributeRepository(Repository):
    """Repository for raw category-attribute relationship data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawCategoryAttribute)

    def get_by_category_key(self, category_key: str) -> list[RawCategoryAttribute]:
        """Get all attributes for a category"""
        result = list(
            self.session.scalars(
                select(RawCategoryAttribute).where(RawCategoryAttribute.category_key == category_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No attributes found for category {category_key}")
        return result

    def find_by_category_key(self, category_key: str) -> list[RawCategoryAttribute]:
        """Find all attributes for a category"""
        return list(
            self.session.scalars(
                select(RawCategoryAttribute).where(RawCategoryAttribute.category_key == category_key)
            ).all()
        )

    def get_by_attribute_key(self, attribute_key: str) -> list[RawCategoryAttribute]:
        """Get all categories for an attribute"""
        result = list(
            self.session.scalars(
                select(RawCategoryAttribute).where(RawCategoryAttribute.attribute_key == attribute_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No categories found for attribute {attribute_key}")
        return result

    def find_by_attribute_key(self, attribute_key: str) -> list[RawCategoryAttribute]:
        """Find all categories for an attribute"""
        return list(
            self.session.scalars(
                select(RawCategoryAttribute).where(RawCategoryAttribute.attribute_key == attribute_key)
            ).all()
        )


class RawProductAttributeValueRepository(Repository):
    """Repository for raw product attribute value data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductAttributeValue)

    def get_by_product_key(self, product_key: str) -> list[RawProductAttributeValue]:
        """Get all attribute values for a product"""
        result = list(
            self.session.scalars(
                select(RawProductAttributeValue).where(RawProductAttributeValue.product_key == product_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No attribute values found for product {product_key}")
        return result

    def find_by_product_key(self, product_key: str) -> list[RawProductAttributeValue]:
        """Find all attribute values for a product"""
        return list(
            self.session.scalars(
                select(RawProductAttributeValue).where(RawProductAttributeValue.product_key == product_key)
            ).all()
        )

    def get_by_attribute_key(self, attribute_key: str) -> list[RawProductAttributeValue]:
        """Get all product values for an attribute"""
        result = list(
            self.session.scalars(
                select(RawProductAttributeValue).where(RawProductAttributeValue.attribute_key == attribute_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No product values found for attribute {attribute_key}")
        return result

    def find_by_attribute_key(self, attribute_key: str) -> list[RawProductAttributeValue]:
        """Find all product values for an attribute"""
        return list(
            self.session.scalars(
                select(RawProductAttributeValue).where(RawProductAttributeValue.attribute_key == attribute_key)
            ).all()
        )


class RawProductAttributeGapRepository(Repository):
    """Repository for raw product attribute gap data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductAttributeGap)

    def get_by_product_key(self, product_key: str) -> list[RawProductAttributeGap]:
        """Get all attribute gaps for a product"""
        result = list(
            self.session.scalars(
                select(RawProductAttributeGap).where(RawProductAttributeGap.product_key == product_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No attribute gaps found for product {product_key}")
        return result

    def find_by_product_key(self, product_key: str) -> list[RawProductAttributeGap]:
        """Find all attribute gaps for a product"""
        return list(
            self.session.scalars(
                select(RawProductAttributeGap).where(RawProductAttributeGap.product_key == product_key)
            ).all()
        )

    def get_by_attribute_key(self, attribute_key: str) -> list[RawProductAttributeGap]:
        """Get all product gaps for an attribute"""
        result = list(
            self.session.scalars(
                select(RawProductAttributeGap).where(RawProductAttributeGap.attribute_key == attribute_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No product gaps found for attribute {attribute_key}")
        return result

    def find_by_attribute_key(self, attribute_key: str) -> list[RawProductAttributeGap]:
        """Find all product gaps for an attribute"""
        return list(
            self.session.scalars(
                select(RawProductAttributeGap).where(RawProductAttributeGap.attribute_key == attribute_key)
            ).all()
        )


class RawProductAttributeAllowableValueRepository(Repository):
    """Repository for raw product attribute allowable value data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductAttributeAllowableValue)

    def get_by_product_key(self, product_key: str) -> list[RawProductAttributeAllowableValue]:
        """Get all allowable values for a product"""
        result = list(
            self.session.scalars(
                select(RawProductAttributeAllowableValue).where(RawProductAttributeAllowableValue.product_key == product_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No allowable values found for product {product_key}")
        return result

    def find_by_product_key(self, product_key: str) -> list[RawProductAttributeAllowableValue]:
        """Find all allowable values for a product"""
        return list(
            self.session.scalars(
                select(RawProductAttributeAllowableValue).where(RawProductAttributeAllowableValue.product_key == product_key)
            ).all()
        )

    def get_by_attribute_key(self, attribute_key: str) -> list[RawProductAttributeAllowableValue]:
        """Get all product allowable values for an attribute"""
        result = list(
            self.session.scalars(
                select(RawProductAttributeAllowableValue).where(RawProductAttributeAllowableValue.attribute_key == attribute_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No product allowable values found for attribute {attribute_key}")
        return result

    def find_by_attribute_key(self, attribute_key: str) -> list[RawProductAttributeAllowableValue]:
        """Find all product allowable values for an attribute"""
        return list(
            self.session.scalars(
                select(RawProductAttributeAllowableValue).where(RawProductAttributeAllowableValue.attribute_key == attribute_key)
            ).all()
        )


class RawCategoryAllowableValueRepository(Repository):
    """Repository for raw category allowable value data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawCategoryAllowableValue)

    def get_by_category_key(self, category_key: str) -> list[RawCategoryAllowableValue]:
        """Get all allowable values for a category"""
        result = list(
            self.session.scalars(
                select(RawCategoryAllowableValue).where(RawCategoryAllowableValue.category_key == category_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No allowable values found for category {category_key}")
        return result

    def find_by_category_key(self, category_key: str) -> list[RawCategoryAllowableValue]:
        """Find all allowable values for a category"""
        return list(
            self.session.scalars(
                select(RawCategoryAllowableValue).where(RawCategoryAllowableValue.category_key == category_key)
            ).all()
        )

    def get_by_attribute_key(self, attribute_key: str) -> list[RawCategoryAllowableValue]:
        """Get all category allowable values for an attribute"""
        result = list(
            self.session.scalars(
                select(RawCategoryAllowableValue).where(RawCategoryAllowableValue.attribute_key == attribute_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No category allowable values found for attribute {attribute_key}")
        return result

    def find_by_attribute_key(self, attribute_key: str) -> list[RawCategoryAllowableValue]:
        """Find all category allowable values for an attribute"""
        return list(
            self.session.scalars(
                select(RawCategoryAllowableValue).where(RawCategoryAllowableValue.attribute_key == attribute_key)
            ).all()
        )


class RawAttributeAllowableValueApplicableInEveryCategoryRepository(Repository):
    """Repository for raw attribute allowable value applicable in every category data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawAttributeAllowableValueApplicableInEveryCategory)

    def get_by_attribute_key(self, attribute_key: str) -> list[RawAttributeAllowableValueApplicableInEveryCategory]:
        """Get all allowable values for an attribute"""
        result = list(
            self.session.scalars(
                select(RawAttributeAllowableValueApplicableInEveryCategory).where(RawAttributeAllowableValueApplicableInEveryCategory.attribute_key == attribute_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No allowable values found for attribute {attribute_key}")
        return result

    def find_by_attribute_key(self, attribute_key: str) -> list[RawAttributeAllowableValueApplicableInEveryCategory]:
        """Find all allowable values for an attribute"""
        return list(
            self.session.scalars(
                select(RawAttributeAllowableValueApplicableInEveryCategory).where(RawAttributeAllowableValueApplicableInEveryCategory.attribute_key == attribute_key)
            ).all()
        )


class RawAttributeAllowableValueInAnyCategoryRepository(Repository):
    """Repository for raw attribute allowable value in any category data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawAttributeAllowableValueInAnyCategory)

    def get_by_attribute_key(self, attribute_key: str) -> list[RawAttributeAllowableValueInAnyCategory]:
        """Get all allowable values for an attribute"""
        result = list(
            self.session.scalars(
                select(RawAttributeAllowableValueInAnyCategory).where(RawAttributeAllowableValueInAnyCategory.attribute_key == attribute_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No allowable values found for attribute {attribute_key}")
        return result

    def find_by_attribute_key(self, attribute_key: str) -> list[RawAttributeAllowableValueInAnyCategory]:
        """Find all allowable values for an attribute"""
        return list(
            self.session.scalars(
                select(RawAttributeAllowableValueInAnyCategory).where(RawAttributeAllowableValueInAnyCategory.attribute_key == attribute_key)
            ).all()
        )


class RawRecommendationRepository(Repository):
    """Repository for raw recommendation data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawRecommendation)

    def get_by_product_key(self, product_key: str) -> list[RawRecommendation]:
        """Get all recommendations for a product"""
        result = list(
            self.session.scalars(
                select(RawRecommendation).where(RawRecommendation.product_key == product_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No recommendations found for product {product_key}")
        return result

    def find_by_product_key(self, product_key: str) -> list[RawRecommendation]:
        """Find all recommendations for a product"""
        return list(
            self.session.scalars(
                select(RawRecommendation).where(RawRecommendation.product_key == product_key)
            ).all()
        )

    def get_by_attribute_key(self, attribute_key: str) -> list[RawRecommendation]:
        """Get all recommendations for an attribute"""
        result = list(
            self.session.scalars(
                select(RawRecommendation).where(RawRecommendation.attribute_key == attribute_key)
            ).all()
        )
        if not result:
            raise ValueError(f"No recommendations found for attribute {attribute_key}")
        return result

    def find_by_attribute_key(self, attribute_key: str) -> list[RawRecommendation]:
        """Find all recommendations for an attribute"""
        return list(
            self.session.scalars(
                select(RawRecommendation).where(RawRecommendation.attribute_key == attribute_key)
            ).all()
        )


class RawRecommendationRoundRepository(Repository):
    """Repository for raw recommendation round data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawRecommendationRound)

    def find_by_round_number(self, round_number: int) -> RawRecommendationRound | None:
        """Find a recommendation round by its round number"""
        return self.session.scalar(
            select(RawRecommendationRound).where(RawRecommendationRound.round_number == round_number)
        )


class RawRichTextSourceRepository(Repository):
    """Repository for raw rich text source data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawRichTextSource)

    def find_by_product_key(self, product_key: str) -> list[RawRichTextSource]:
        """Find all rich text sources for a product"""
        return list(
            self.session.scalars(
                select(RawRichTextSource).where(RawRichTextSource.product_key == product_key)
            ).all()
        ) 