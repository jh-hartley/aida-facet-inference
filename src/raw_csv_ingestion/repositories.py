from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.raw_csv_ingestion.records import (
    PredictionExperimentRecord,
    PredictionResultRecord,
    RawAttributeAllowableValueApplicableInEveryCategoryRecord,
    RawAttributeAllowableValueInAnyCategoryRecord,
    RawAttributeRecord,
    RawCategoryAllowableValueRecord,
    RawCategoryAttributeRecord,
    RawCategoryRecord,
    RawProductAttributeAllowableValueRecord,
    RawProductAttributeGapRecord,
    RawProductAttributeValueRecord,
    RawProductCategoryRecord,
    RawProductRecord,
    RawRecommendationRecord,
    RawRichTextSourceRecord,
)

T = TypeVar("T", bound=Any)

GloballyAllowedValueRecord = (
    RawAttributeAllowableValueApplicableInEveryCategoryRecord
)


class Repository(Generic[T]):
    """Repository class with common functionality"""

    def __init__(self, session: Session, model: Type[T]):
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


class RawProductRepository(Repository[RawProductRecord]):
    """Repository for raw product data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductRecord)

    def get_by_system_name(self, system_name: str) -> RawProductRecord:
        result = self.session.scalar(
            select(RawProductRecord).where(
                RawProductRecord.system_name == system_name
            )
        )
        if result is None:
            raise ValueError(
                f"No product found with system name {system_name}"
            )
        return result

    def find_by_system_name(self, system_name: str) -> RawProductRecord | None:
        return self.session.scalar(
            select(RawProductRecord).where(
                RawProductRecord.system_name == system_name
            )
        )


class RawCategoryRepository(Repository[RawCategoryRecord]):
    """Repository for raw category data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawCategoryRecord)

    def get_by_system_name(self, system_name: str) -> RawCategoryRecord:
        result = self.session.scalar(
            select(RawCategoryRecord).where(
                RawCategoryRecord.system_name == system_name
            )
        )
        if result is None:
            raise ValueError(
                f"No category found with system name {system_name}"
            )
        return result

    def find_by_system_name(
        self, system_name: str
    ) -> RawCategoryRecord | None:
        return self.session.scalar(
            select(RawCategoryRecord).where(
                RawCategoryRecord.system_name == system_name
            )
        )


class RawAttributeRepository(Repository[RawAttributeRecord]):
    """Repository for raw attribute data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawAttributeRecord)

    def get_by_system_name(self, system_name: str) -> RawAttributeRecord:
        result = self.session.scalar(
            select(RawAttributeRecord).where(
                RawAttributeRecord.system_name == system_name
            )
        )
        if result is None:
            raise ValueError(
                f"No attribute found with system name {system_name}"
            )
        return result

    def find_by_system_name(
        self, system_name: str
    ) -> RawAttributeRecord | None:
        return self.session.scalar(
            select(RawAttributeRecord).where(
                RawAttributeRecord.system_name == system_name
            )
        )

    def get_by_friendly_name(self, friendly_name: str) -> RawAttributeRecord:
        """Get an attribute by its friendly name"""
        result = self.session.scalar(
            select(RawAttributeRecord).where(
                RawAttributeRecord.friendly_name == friendly_name
            )
        )
        if result is None:
            raise ValueError(
                f"No attribute found with friendly name {friendly_name}"
            )
        return result


class RawProductCategoryRepository(Repository[RawProductCategoryRecord]):
    """Repository for raw product-category relationship data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductCategoryRecord)

    def get_by_product_key(
        self, product_key: str
    ) -> list[RawProductCategoryRecord]:
        result = list(
            self.session.scalars(
                select(RawProductCategoryRecord).where(
                    RawProductCategoryRecord.product_key == product_key
                )
            ).all()
        )
        if not result:
            raise ValueError(f"No categories found for product {product_key}")
        return result

    def find_by_product_key(
        self, product_key: str
    ) -> list[RawProductCategoryRecord]:
        return list(
            self.session.scalars(
                select(RawProductCategoryRecord).where(
                    RawProductCategoryRecord.product_key == product_key
                )
            ).all()
        )

    def get_by_category_key(
        self, category_key: str
    ) -> list[RawProductCategoryRecord]:
        result = list(
            self.session.scalars(
                select(RawProductCategoryRecord).where(
                    RawProductCategoryRecord.category_key == category_key
                )
            ).all()
        )
        if not result:
            raise ValueError(f"No products found in category {category_key}")
        return result

    def find_by_category_key(
        self, category_key: str
    ) -> list[RawProductCategoryRecord]:
        return list(
            self.session.scalars(
                select(RawProductCategoryRecord).where(
                    RawProductCategoryRecord.category_key == category_key
                )
            ).all()
        )

    def find_by_product_key_and_category_key(
        self, product_key: str, category_key: str
    ) -> RawProductCategoryRecord | None:
        return self.session.scalar(
            select(RawProductCategoryRecord).where(
                RawProductCategoryRecord.product_key == product_key,
                RawProductCategoryRecord.category_key == category_key,
            )
        )


class RawCategoryAttributeRepository(Repository[RawCategoryAttributeRecord]):
    """Repository for raw category-attribute relationship data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawCategoryAttributeRecord)

    def get_by_category_key(
        self, category_key: str
    ) -> list[RawCategoryAttributeRecord]:
        result = list(
            self.session.scalars(
                select(RawCategoryAttributeRecord).where(
                    RawCategoryAttributeRecord.category_key == category_key
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
    ) -> list[RawCategoryAttributeRecord]:
        return list(
            self.session.scalars(
                select(RawCategoryAttributeRecord).where(
                    RawCategoryAttributeRecord.category_key == category_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawCategoryAttributeRecord]:
        result = list(
            self.session.scalars(
                select(RawCategoryAttributeRecord).where(
                    RawCategoryAttributeRecord.attribute_key == attribute_key
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
    ) -> list[RawCategoryAttributeRecord]:
        return list(
            self.session.scalars(
                select(RawCategoryAttributeRecord).where(
                    RawCategoryAttributeRecord.attribute_key == attribute_key
                )
            ).all()
        )

    def find_by_category_key_and_attribute_key(
        self, category_key: str, attribute_key: str
    ) -> RawCategoryAttributeRecord | None:
        return self.session.scalar(
            select(RawCategoryAttributeRecord).where(
                RawCategoryAttributeRecord.category_key == category_key,
                RawCategoryAttributeRecord.attribute_key == attribute_key,
            )
        )


class RawProductAttributeValueRepository(
    Repository[RawProductAttributeValueRecord]
):
    """Repository for raw product attribute value data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductAttributeValueRecord)

    def get_by_product_key(
        self, product_key: str
    ) -> list[RawProductAttributeValueRecord]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeValueRecord).where(
                    RawProductAttributeValueRecord.product_key == product_key
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
    ) -> list[RawProductAttributeValueRecord]:
        return list(
            self.session.scalars(
                select(RawProductAttributeValueRecord).where(
                    RawProductAttributeValueRecord.product_key == product_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawProductAttributeValueRecord]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeValueRecord).where(
                    RawProductAttributeValueRecord.attribute_key
                    == attribute_key
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
    ) -> list[RawProductAttributeValueRecord]:
        return list(
            self.session.scalars(
                select(RawProductAttributeValueRecord).where(
                    RawProductAttributeValueRecord.attribute_key
                    == attribute_key
                )
            ).all()
        )

    def find_by_product_key_and_attribute_key_and_value(
        self, product_key: str, attribute_key: str, value: str
    ) -> RawProductAttributeValueRecord | None:
        return self.session.scalar(
            select(RawProductAttributeValueRecord).where(
                RawProductAttributeValueRecord.product_key == product_key,
                RawProductAttributeValueRecord.attribute_key == attribute_key,
                RawProductAttributeValueRecord.value == value,
            )
        )


class RawProductAttributeGapRepository(
    Repository[RawProductAttributeGapRecord]
):
    """Repository for raw product attribute gap data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawProductAttributeGapRecord)

    def get_by_product_key(
        self, product_key: str
    ) -> list[RawProductAttributeGapRecord]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeGapRecord).where(
                    RawProductAttributeGapRecord.product_key == product_key
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
    ) -> list[RawProductAttributeGapRecord]:
        return list(
            self.session.scalars(
                select(RawProductAttributeGapRecord).where(
                    RawProductAttributeGapRecord.product_key == product_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawProductAttributeGapRecord]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeGapRecord).where(
                    RawProductAttributeGapRecord.attribute_key == attribute_key
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
    ) -> list[RawProductAttributeGapRecord]:
        return list(
            self.session.scalars(
                select(RawProductAttributeGapRecord).where(
                    RawProductAttributeGapRecord.attribute_key == attribute_key
                )
            ).all()
        )

    def find_by_product_key_and_attribute_key(
        self, product_key: str, attribute_key: str
    ) -> RawProductAttributeGapRecord | None:
        return self.session.scalar(
            select(RawProductAttributeGapRecord).where(
                RawProductAttributeGapRecord.product_key == product_key,
                RawProductAttributeGapRecord.attribute_key == attribute_key,
            )
        )


class RawProductAttributeAllowableValueRepository(
    Repository[RawProductAttributeAllowableValueRecord]
):
    """
    Repository for raw product attribute allowable value data from CSV
    """

    def __init__(self, session: Session):
        super().__init__(session, RawProductAttributeAllowableValueRecord)

    def get_by_product_key(
        self, product_key: str
    ) -> list[RawProductAttributeAllowableValueRecord]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeAllowableValueRecord).where(
                    RawProductAttributeAllowableValueRecord.product_key
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
    ) -> list[RawProductAttributeAllowableValueRecord]:
        """Find all allowable values for a product"""
        return list(
            self.session.scalars(
                select(RawProductAttributeAllowableValueRecord).where(
                    RawProductAttributeAllowableValueRecord.product_key
                    == product_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawProductAttributeAllowableValueRecord]:
        result = list(
            self.session.scalars(
                select(RawProductAttributeAllowableValueRecord).where(
                    RawProductAttributeAllowableValueRecord.attribute_key
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
    ) -> list[RawProductAttributeAllowableValueRecord]:
        """Find all product allowable values for an attribute"""
        return list(
            self.session.scalars(
                select(RawProductAttributeAllowableValueRecord).where(
                    RawProductAttributeAllowableValueRecord.attribute_key
                    == attribute_key
                )
            ).all()
        )

    def find_by_product_key_and_attribute_key(
        self, product_key: str, attribute_key: str
    ) -> list[RawProductAttributeAllowableValueRecord]:
        """
        Find all allowable values for a specific product-attribute combination
        """
        return list(
            self.session.scalars(
                select(RawProductAttributeAllowableValueRecord).where(
                    RawProductAttributeAllowableValueRecord.product_key
                    == product_key,
                    RawProductAttributeAllowableValueRecord.attribute_key
                    == attribute_key,
                )
            ).all()
        )

    def find_by_product_key_and_attribute_key_and_value(
        self, product_key: str, attribute_key: str, value: str
    ) -> RawProductAttributeAllowableValueRecord | None:
        return self.session.scalar(
            select(RawProductAttributeAllowableValueRecord).where(
                RawProductAttributeAllowableValueRecord.product_key
                == product_key,
                RawProductAttributeAllowableValueRecord.attribute_key
                == attribute_key,
                RawProductAttributeAllowableValueRecord.value == value,
            )
        )


class RawCategoryAllowableValueRepository(
    Repository[RawCategoryAllowableValueRecord]
):
    """Repository for raw category allowable value data from CSV"""

    def __init__(self, session: Session):
        super().__init__(session, RawCategoryAllowableValueRecord)

    def get_by_category_key(
        self, category_key: str
    ) -> list[RawCategoryAllowableValueRecord]:
        result = list(
            self.session.scalars(
                select(RawCategoryAllowableValueRecord).where(
                    RawCategoryAllowableValueRecord.category_key
                    == category_key
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
    ) -> list[RawCategoryAllowableValueRecord]:
        return list(
            self.session.scalars(
                select(RawCategoryAllowableValueRecord).where(
                    RawCategoryAllowableValueRecord.category_key
                    == category_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawCategoryAllowableValueRecord]:
        result = list(
            self.session.scalars(
                select(RawCategoryAllowableValueRecord).where(
                    RawCategoryAllowableValueRecord.attribute_key
                    == attribute_key
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
    ) -> list[RawCategoryAllowableValueRecord]:
        return list(
            self.session.scalars(
                select(RawCategoryAllowableValueRecord).where(
                    RawCategoryAllowableValueRecord.attribute_key
                    == attribute_key
                )
            ).all()
        )

    def find_by_category_key_and_attribute_key_and_value(
        self, category_key: str, attribute_key: str, value: str
    ) -> RawCategoryAllowableValueRecord | None:
        return self.session.scalar(
            select(RawCategoryAllowableValueRecord).where(
                RawCategoryAllowableValueRecord.category_key == category_key,
                RawCategoryAllowableValueRecord.attribute_key == attribute_key,
                RawCategoryAllowableValueRecord.value == value,
            )
        )


class RawRecommendationRepository(Repository[RawRecommendationRecord]):
    """Repository for raw recommendation data"""

    def __init__(self, session: Session):
        super().__init__(session, RawRecommendationRecord)

    def get_by_product_key(
        self, product_key: str
    ) -> list[RawRecommendationRecord]:
        result = list(
            self.session.scalars(
                select(RawRecommendationRecord).where(
                    RawRecommendationRecord.product_key == product_key
                )
            ).all()
        )
        if not result:
            raise ValueError(
                f"No recommendations found for product {product_key}"
            )
        return result

    def find_by_product_key(
        self, product_key: str
    ) -> list[RawRecommendationRecord]:
        return list(
            self.session.scalars(
                select(RawRecommendationRecord).where(
                    RawRecommendationRecord.product_key == product_key
                )
            ).all()
        )

    def get_by_attribute_key(
        self, attribute_key: str
    ) -> list[RawRecommendationRecord]:
        result = list(
            self.session.scalars(
                select(RawRecommendationRecord).where(
                    RawRecommendationRecord.attribute_key == attribute_key
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
    ) -> list[RawRecommendationRecord]:
        return list(
            self.session.scalars(
                select(RawRecommendationRecord).where(
                    RawRecommendationRecord.attribute_key == attribute_key
                )
            ).all()
        )

    def find_by_product_key_and_attribute_key_and_value(
        self, product_key: str, attribute_key: str, value: str
    ) -> RawRecommendationRecord | None:
        return self.session.scalar(
            select(RawRecommendationRecord).where(
                RawRecommendationRecord.product_key == product_key,
                RawRecommendationRecord.attribute_key == attribute_key,
                RawRecommendationRecord.value == value,
            )
        )


class RawRichTextSourceRepository(Repository[RawRichTextSourceRecord]):
    """Repository for raw rich text source data"""

    def __init__(self, session: Session):
        super().__init__(session, RawRichTextSourceRecord)

    def find_by_product_key(
        self, product_key: str
    ) -> list[RawRichTextSourceRecord]:
        """Find all rich text sources for a product"""
        return list(
            self.session.scalars(
                select(RawRichTextSourceRecord).where(
                    RawRichTextSourceRecord.product_key == product_key
                )
            ).all()
        )

    def find_by_product_key_and_name(
        self, product_key: str, name: str
    ) -> RawRichTextSourceRecord | None:
        return self.session.scalar(
            select(RawRichTextSourceRecord).where(
                RawRichTextSourceRecord.product_key == product_key,
                RawRichTextSourceRecord.name == name,
            )
        )


class RawAttributeAllowableValueApplicableInEveryCategoryRepository(
    Repository[GloballyAllowedValueRecord]
):
    """Repository for attribute values that are valid in every category"""

    def __init__(self, session: Session):
        super().__init__(session, GloballyAllowedValueRecord)

    def find_by_attribute_key_and_value(
        self, attribute_key: str, value: str
    ) -> GloballyAllowedValueRecord | None:
        return self.session.scalar(
            select(GloballyAllowedValueRecord).where(
                GloballyAllowedValueRecord.attribute_key == attribute_key,
                GloballyAllowedValueRecord.value == value,
            )
        )


class RawAttributeAllowableValueInAnyCategoryRepository(
    Repository[RawAttributeAllowableValueInAnyCategoryRecord]
):
    """Repository for attribute values that are valid in any category"""

    def __init__(self, session: Session):
        super().__init__(
            session, RawAttributeAllowableValueInAnyCategoryRecord
        )

    def find_by_attribute_key_and_value(
        self, attribute_key: str, value: str
    ) -> RawAttributeAllowableValueInAnyCategoryRecord | None:
        return self.session.scalar(
            select(RawAttributeAllowableValueInAnyCategoryRecord).where(
                RawAttributeAllowableValueInAnyCategoryRecord.attribute_key
                == attribute_key,
                RawAttributeAllowableValueInAnyCategoryRecord.value == value,
            )
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
