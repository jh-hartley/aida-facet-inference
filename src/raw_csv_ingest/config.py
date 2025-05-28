from src.raw_csv_ingest.models import (
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
)
from src.raw_csv_ingest.uow import (
    create_attribute,
    create_category,
    create_category_allowable_value,
    create_category_attribute,
    create_product,
    create_product_attribute_allowable_value,
    create_product_attribute_gap,
    create_product_attribute_value,
    create_product_category,
    create_recommendation,
)


class CSVConfig:
    """Configuration for CSV file processing"""

    FILE_CONFIGS = {
        "Product.csv": {
            "model": RawProduct,
            "create_func": create_product,
        },
        "Category.csv": {
            "model": RawCategory,
            "create_func": create_category,
        },
        "Attribute.csv": {
            "model": RawAttribute,
            "create_func": create_attribute,
        },
        "ProductCategory.csv": {
            "model": RawProductCategory,
            "create_func": create_product_category,
        },
        "CategoryAttribute.csv": {
            "model": RawCategoryAttribute,
            "create_func": create_category_attribute,
        },
        "ProductAttributeValue.csv": {
            "model": RawProductAttributeValue,
            "create_func": create_product_attribute_value,
        },
        "ProductAttributeGap.csv": {
            "model": RawProductAttributeGap,
            "create_func": create_product_attribute_gap,
        },
        "ProductAttributeAllowableValue.csv": {
            "model": RawProductAttributeAllowableValue,
            "create_func": create_product_attribute_allowable_value,
        },
        "CategoryAllowableValue.csv": {
            "model": RawCategoryAllowableValue,
            "create_func": create_category_allowable_value,
        },
        "Recommendation.csv": {
            "model": RawRecommendation,
            "create_func": create_recommendation,
        },
    }
