from raw_csv_ingest.records import (
    RawAttributeRecord,
    RawCategoryRecord,
    RawCategoryAllowableValueRecord,
    RawCategoryAttributeRecord,
    RawProductRecord,
    RawProductAttributeAllowableValueRecord,
    RawProductAttributeGapRecord,
    RawProductAttributeValueRecord,
    RawProductCategoryRecord,
    RawRecommendationRecord,
    RawRichTextSourceRecord,
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
    create_rich_text_source,
)


class CSVConfig:
    """Configuration for CSV file processing"""

    FILE_CONFIGS = {
        "Product.csv": {
            "model": RawProductRecord,
            "create_func": create_product,
            "column_mapping": {
                "ProductKey": "product_key",
                "SystemName": "system_name",
                "FriendlyName": "friendly_name",
            },
        },
        "Category.csv": {
            "model": RawCategoryRecord,
            "create_func": create_category,
            "column_mapping": {
                "CategoryKey": "category_key",
                "SystemName": "system_name",
                "FriendlyName": "friendly_name",
            },
        },
        "Attribute.csv": {
            "model": RawAttributeRecord,
            "create_func": create_attribute,
            "column_mapping": {
                "AttributeKey": "attribute_key",
                "SystemName": "system_name",
                "FriendlyName": "friendly_name",
                "AttributeType": "attribute_type",
                "UnitMeasureType": "unit_measure_type",
            },
        },
        "ProductCategory.csv": {
            "model": RawProductCategoryRecord,
            "create_func": create_product_category,
            "column_mapping": {
                "ProductKey": "product_key",
                "CategoryKey": "category_key",
            },
        },
        "CategoryAttribute.csv": {
            "model": RawCategoryAttributeRecord,
            "create_func": create_category_attribute,
            "column_mapping": {
                "CategoryAttributeKey": "category_attribute_key",
                "CategoryKey": "category_key",
                "AttributeKey": "attribute_key",
            },
        },
        "ProductAttributeValue.csv": {
            "model": RawProductAttributeValueRecord,
            "create_func": create_product_attribute_value,
            "column_mapping": {
                "ProductKey": "product_key",
                "AttributeKey": "attribute_key",
                "Value": "value",
            },
        },
        "ProductAttributeGaps.csv": {
            "model": RawProductAttributeGapRecord,
            "create_func": create_product_attribute_gap,
            "column_mapping": {
                "ProductKey": "product_key",
                "AttributeKey": "attribute_key",
            },
        },
        "ProductAttributeAllowableValue.csv": {
            "model": RawProductAttributeAllowableValueRecord,
            "create_func": create_product_attribute_allowable_value,
            "column_mapping": {
                "ProductKey": "product_key",
                "AttributeKey": "attribute_key",
                "Value": "value",
            },
        },
        "CategoryAllowableValue.csv": {
            "model": RawCategoryAllowableValueRecord,
            "create_func": create_category_allowable_value,
            "column_mapping": {
                "CategoryAttributeKey": "category_attribute_key",
                "AllowableValue": "value",
                "AllowableUnitType": "unit_type",
                "MinimumValue": "minimum_value",
                "MinimumUnit": "minimum_unit",
                "MaximumValue": "maximum_value",
                "MaximumUnit": "maximum_unit",
                "RangeQualifierEnum": "range_qualifier",
            },
        },
        "Recommendation.csv": {
            "model": RawRecommendationRecord,
            "create_func": create_recommendation,
            "column_mapping": {
                "ProductKey": "product_key",
                "AttributeKey": "attribute_key",
                "RecommendedValue": "value",
                "ConfidenceScore": "confidence",
            },
        },
        "RichTextSource.csv": {
            "model": RawRichTextSourceRecord,
            "create_func": create_rich_text_source,
            "column_mapping": {
                "ProductKey": "product_key",
                "RichText": "content",
                "RichTextName": "name",
                "RichTextPriority": "priority",
            },
        },
    }
