from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.infrastructure.database.models import ProductDetails, ProductGaps
from core.infrastructure.database.predictions.records import (
    PredictionExperimentRecord,
    PredictionResultRecord,
)
from src.core.infrastructure.database.types import (
    ProductAttributeGap,
    ProductAttributeValue,
    ProductDescriptor,
)
from src.core.infrastructure.database.input_data.records import (
    HumanRecommendationRecord,
    RawAttributeAllowableValueApplicableInEveryCategoryRecord,
    RawAttributeAllowableValueInAnyCategoryRecord,
    RawAttributeRecord,
    RawCategoryAllowableValueRecord,
    RawCategoryRecord,
    RawProductAttributeGapRecord,
    RawProductAttributeValueRecord,
    RawProductCategoryRecord,
    RawProductRecord,
    RawRecommendationRecord,
    RawRichTextSourceRecord,
)
from src.core.infrastructure.database.input_data.repositories import (
    RawAttributeRepository,
    RawCategoryAllowableValueRepository,
    RawCategoryRepository,
    RawProductAttributeGapRepository,
    RawProductAttributeValueRepository,
    RawProductCategoryRepository,
    RawProductRepository,
    RawRichTextSourceRepository,
    Repository,
)

# Type aliases for long record names
GloballyAllowedValueRecord = (
    RawAttributeAllowableValueApplicableInEveryCategoryRecord
)
SharedAllowedValueRecord = RawAttributeAllowableValueInAnyCategoryRecord


class FacetIdentificationRepository:
    """
    Repository for retrieving complete product information in domain model
    format
    """

    def __init__(self, session: Session):
        self.session = session
        self.product_repo = RawProductRepository(session)
        self.category_repo = RawCategoryRepository(session)
        self.attribute_repo = RawAttributeRepository(session)
        self.product_category_repo = RawProductCategoryRepository(session)
        self.product_attribute_value_repo = RawProductAttributeValueRepository(
            session
        )
        self.rich_text_repo = RawRichTextSourceRepository(session)
        self.product_attribute_gap_repo = RawProductAttributeGapRepository(
            session
        )
        self.category_allowable_value_repo = (
            RawCategoryAllowableValueRepository(session)
        )

    def _get_allowable_values_for_attribute(
        self, category_keys: list[str], attribute_key: str
    ) -> set[str]:
        """Get all allowable values for an attribute across categories"""
        category_values = set(
            av.value
            for av in self.session.scalars(
                select(RawCategoryAllowableValueRecord).where(
                    RawCategoryAllowableValueRecord.category_key.in_(
                        category_keys
                    ),
                    RawCategoryAllowableValueRecord.attribute_key
                    == attribute_key,
                )
            ).all()
        )

        global_values = set(
            av.value
            for av in self.session.scalars(
                select(GloballyAllowedValueRecord).where(
                    GloballyAllowedValueRecord.attribute_key == attribute_key
                )
            ).all()
        )

        any_category_values = set(
            av.value
            for av in self.session.scalars(
                select(SharedAllowedValueRecord).where(
                    SharedAllowedValueRecord.attribute_key == attribute_key
                )
            ).all()
        )

        return category_values | global_values | any_category_values

    def get_product_details(self, product_key: str) -> ProductDetails:
        """
        Get complete information about a product including categories,
        attributes, and rich text in a format suitable for LLM consumption.

        Raises:
            ValueError: If product is not found
        """
        product = self.product_repo.get_by_id(product_key)

        categories = [
            cat.friendly_name
            for cat in self.session.scalars(
                select(RawCategoryRecord)
                .join(
                    RawProductCategoryRecord,
                    RawCategoryRecord.category_key
                    == RawProductCategoryRecord.category_key,
                )
                .where(RawProductCategoryRecord.product_key == product_key)
            ).all()
        ]

        attributes = [
            ProductAttributeValue(
                attribute=attr.friendly_name, value=val.value
            )
            for attr, val in self.session.execute(
                select(RawAttributeRecord, RawProductAttributeValueRecord)
                .join(
                    RawProductAttributeValueRecord,
                    RawAttributeRecord.attribute_key
                    == RawProductAttributeValueRecord.attribute_key,
                )
                .where(
                    RawProductAttributeValueRecord.product_key == product_key
                )
            ).all()
        ]

        descriptions = [
            ProductDescriptor(descriptor=rt.name, value=rt.content)
            for rt in self.session.scalars(
                select(RawRichTextSourceRecord)
                .where(RawRichTextSourceRecord.product_key == product_key)
                .order_by(RawRichTextSourceRecord.priority)
            ).all()
        ]

        return ProductDetails(
            product_key=product.product_key,
            product_code=product.system_name,
            product_name=product.friendly_name,
            product_description=descriptions,
            categories=categories,
            attributes=attributes,
            code_type=product.code_type,
        )

    def find_product_details(self, product_key: str) -> ProductDetails | None:
        """
        Find complete information about a product including categories,
        attributes, and rich text in a format suitable for LLM consumption.

        Returns:
            ProductDetails if found, None otherwise
        """
        try:
            return self.get_product_details(product_key)
        except ValueError:
            return None

    def get_product_gaps(self, product_key: str) -> ProductGaps:
        """
        Get all attributes a product is missing and their possible values
        in an object suitable for LLM consumption.

        Raises:
            ValueError: If product is not found
        """
        product = self.product_repo.get_by_id(product_key)

        product_categories = self.product_category_repo.get_by_product_key(
            product_key
        )
        category_keys = [pc.category_key for pc in product_categories]

        gaps = self.product_attribute_gap_repo.get_by_product_key(product_key)

        gap_details = []
        for gap in gaps:
            allowable_values = self._get_allowable_values_for_attribute(
                category_keys, gap.attribute_key
            )

            if allowable_values:
                attribute = self.attribute_repo.get_by_id(gap.attribute_key)
                gap_details.append(
                    ProductAttributeGap(
                        attribute=attribute.friendly_name,
                        allowable_values=sorted(allowable_values),
                    )
                )

        return ProductGaps(
            product_code=product.product_key,
            product_name=product.friendly_name,
            gaps=gap_details,
        )

    def find_product_gaps(self, product_key: str) -> ProductGaps | None:
        """
        Find information about missing attribute values for a product and their
        possible values based on category rules.

        Returns:
            ProductGaps if found, None otherwise
        """
        try:
            return self.get_product_gaps(product_key)
        except ValueError:
            return None

    def get_product_gaps_with_ground_truth(
        self, product_key: str
    ) -> list[tuple[ProductAttributeGap, str | None]]:
        """
        Get all gaps for a product along with their ground truth values from
        recommendations.

        Returns:
            A list of tuples containing (gap, ground_truth_value). The ground
            truth value will be None if no recommendation exists.

        Raises:
            ValueError: If product is not found
        """
        gaps = self.get_product_gaps(product_key)
        recommendations = self.session.scalars(
            select(RawRecommendationRecord).where(
                RawRecommendationRecord.product_key == product_key
            )
        ).all()

        recommendation_lookup = {
            rec.attribute_key: rec.value for rec in recommendations
        }

        return [
            (
                gap,
                recommendation_lookup.get(
                    self.attribute_repo.get_by_friendly_name(
                        gap.attribute
                    ).attribute_key
                ),
            )
            for gap in gaps.gaps
        ]

    def get_products_with_gaps(self) -> list[str]:
        """
        Get a list of all product keys that have at least one attribute gap.

        Returns:
            List of product keys that have gaps
        """
        return list(
            self.session.scalars(
                select(RawProductAttributeGapRecord.product_key).distinct()
            ).all()
        )

    def get_products_without_gaps(self) -> list[str]:
        """
        Get a list of all product keys that have no attribute gaps.

        Returns:
            List of product keys that have no gaps
        """
        # Get all product keys that have gaps
        products_with_gaps = set(
            self.session.scalars(
                select(RawProductAttributeGapRecord.product_key).distinct()
            ).all()
        )

        # Get products that are not in that set
        return list(
            self.session.scalars(
                select(RawProductRecord.product_key).where(
                    RawProductRecord.product_key.not_in(products_with_gaps)
                )
            ).all()
        )

    def get_single_product(self, with_gaps: bool | None = None) -> str | None:
        """
        Get a single product key from the database.

        Args:
            with_gaps: If True, returns a product with gaps.
                      If False, returns a product without gaps.
                      If None, returns any product.

        Returns:
            A product key if found, None otherwise
        """
        if with_gaps is None:
            return self.session.scalar(
                select(RawProductRecord.product_key).limit(1)
            )

        if with_gaps:
            return self.session.scalar(
                select(RawProductAttributeGapRecord.product_key)
                .distinct()
                .limit(1)
            )

        # Get a product without gaps
        products_with_gaps = set(
            self.session.scalars(
                select(RawProductAttributeGapRecord.product_key).distinct()
            ).all()
        )

        return self.session.scalar(
            select(RawProductRecord.product_key)
            .where(RawProductRecord.product_key.not_in(products_with_gaps))
            .limit(1)
        )

    def get_product_gaps_from_recommendations(
        self, product_key: str
    ) -> ProductGaps:
        """
        Get gaps for a product based on accepted recommendations.
        This is used for evaluation purposes where we only want to predict
        for attributes that have accepted recommendations.

        Args:
            product_key: The product key to get gaps for

        Returns:
            ProductGaps object containing only the gaps that
                have accepted recommendations

        Raises:
            ValueError: If product is not found
        """
        # Get the product to get its system_name
        product = self.product_repo.get_by_id(product_key)

        # Get accepted recommendations for this product
        recommendations = self.session.scalars(
            select(HumanRecommendationRecord).where(
                HumanRecommendationRecord.product_reference
                == product.system_name,
                HumanRecommendationRecord.action == "Accept Recommendation",
            )
        ).all()

        # Get product categories for allowable values
        product_categories = self.product_category_repo.get_by_product_key(
            product_key
        )
        category_keys = [pc.category_key for pc in product_categories]

        # Create gaps from recommendations
        gap_details = []
        for rec in recommendations:
            # Get attribute key from system name
            attribute = self.session.scalars(
                select(RawAttributeRecord).where(
                    RawAttributeRecord.system_name == rec.attribute_reference
                )
            ).first()

            if attribute:
                # Get allowable values for this attribute
                allowable_values = self._get_allowable_values_for_attribute(
                    category_keys, attribute.attribute_key
                )

                if allowable_values:
                    gap_details.append(
                        ProductAttributeGap(
                            attribute=attribute.friendly_name,
                            allowable_values=sorted(allowable_values),
                        )
                    )

        return ProductGaps(
            product_code=product.product_key,
            product_name=product.friendly_name,
            gaps=gap_details,
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
