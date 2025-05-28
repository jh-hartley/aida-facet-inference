from pydantic import BaseModel

from src.types_ import (
    AttributeMappingView,
    ProductEmbeddingView,
    ProductView,
    RetailerFacetView,
    RetailerProductAttributeView,
    RetailerProductView,
    RetailerView,
    RetailerCategoryView,
)


class ProductWithRetailers(ProductView):
    """A product with its associated retailers"""

    retailers: list[RetailerProductView]


class RetailerWithProducts(RetailerView):
    """A retailer with its associated products"""

    products: list[RetailerProductView]


class ProductWithEmbedding(ProductView):
    """A product with its embedding"""

    embedding: ProductEmbeddingView | None = None


class RetailerWithFacets(RetailerView):
    """A retailer with its associated facets"""

    facets: list[RetailerFacetView]


class RetailerCategoryTree(RetailerCategoryView):
    """A complete category tree with facets for a retailer"""

    children: list["RetailerCategoryTree"] = []

    class Config:
        from_attributes = True


class RetailerProductWithAttributes(RetailerProductView):
    """A retailer product with its attributes"""

    attributes: list[RetailerProductAttributeView]


class RetailerWithMappings(RetailerView):
    """A retailer with its attribute mappings"""

    mappings: list[AttributeMappingView]


class ProductSearchResult(BaseModel):
    """Search result for products"""

    product: ProductView
    similarity_score: float


class RetailerSearchResult(BaseModel):
    """Search result for retailers"""

    retailer: RetailerView
    similarity_score: float


class RetailerFacetSearchResult(BaseModel):
    """Search result for retailer facets"""

    facet: RetailerFacetView
    similarity_score: float


# Update forward references
RetailerCategoryTree.update_forward_refs()
