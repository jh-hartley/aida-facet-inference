from pydantic import BaseModel

from src.core.domain.models import ProductDetails
from src.core.domain.repositories import FacetIdentificationRepository


class FacetPredictionTarget(BaseModel):
    """Target data for facet prediction, including ground truth values."""

    attribute: str
    allowable_values: list[str]
    ground_truth: str

    @property
    def has_ground_truth(self) -> bool:
        """Whether this target has a non-empty ground truth value."""
        return bool(self.ground_truth)


class FacetInferenceSample(BaseModel):
    """A single sample for facet inference training/evaluation."""

    product_details: ProductDetails
    gaps: list[FacetPredictionTarget]

    @property
    def has_ground_truth(self) -> bool:
        """Whether this sample has any ground truth values."""
        return any(gap.has_ground_truth for gap in self.gaps)

    @property
    def num_gaps(self) -> int:
        """Number of gaps in this sample."""
        return len(self.gaps)


class FacetInferenceDataset(BaseModel):
    """A dataset of samples for facet inference."""

    samples: list[FacetInferenceSample]

    @property
    def num_samples(self) -> int:
        """Number of samples in the dataset."""
        return len(self.samples)

    @property
    def num_gaps(self) -> int:
        """Total number of gaps across all samples."""
        return sum(sample.num_gaps for sample in self.samples)

    @property
    def num_gaps_with_ground_truth(self) -> int:
        """Number of gaps that have ground truth values."""
        return sum(
            sum(1 for gap in sample.gaps if gap.has_ground_truth)
            for sample in self.samples
        )

    def get_samples_with_ground_truth(self) -> "FacetInferenceDataset":
        """
        Get a new dataset containing only samples with ground truth values.
        """
        return FacetInferenceDataset(
            samples=[s for s in self.samples if s.has_ground_truth]
        )


class FacetInferenceDataLoader:
    """Data loader for facet inference training and evaluation."""

    def __init__(self, repository: "FacetIdentificationRepository"):
        self.repository = repository

    def load_dataset(self, product_keys: list[str]) -> FacetInferenceDataset:
        """
        Load a dataset of samples for the given product keys.

        Args:
            product_keys: List of product keys to load data for

        Returns:
            A dataset containing samples for each product
        """
        samples = []
        for product_key in product_keys:
            try:
                product_details = self.repository.get_product_details(
                    product_key
                )

                gaps_with_truth = (
                    self.repository.get_product_gaps_with_ground_truth(
                        product_key
                    )
                )

                prediction_targets = [
                    FacetPredictionTarget(
                        attribute=gap.attribute,
                        allowable_values=gap.allowable_values,
                        ground_truth=ground_truth
                        or "",  # Convert None to empty string
                    )
                    for gap, ground_truth in gaps_with_truth
                ]

                sample = FacetInferenceSample(
                    product_details=product_details,
                    gaps=prediction_targets,
                )
                samples.append(sample)

            except ValueError as e:
                print(f"Warning: Could not load product {product_key}: {e}")
                continue

        return FacetInferenceDataset(samples=samples)

    def load_evaluation_dataset(self) -> FacetInferenceDataset:
        """
        Load a dataset of all products with gaps that have ground truth values.

        Returns:
            A dataset containing only samples with ground truth values
        """
        product_keys = self.repository.get_products_with_gaps()

        dataset = self.load_dataset(product_keys)

        return dataset.get_samples_with_ground_truth()
