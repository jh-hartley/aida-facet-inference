from src.csv_ingestion.records import (
    HumanRecommendationRecord,
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
from src.csv_ingestion.uow import (
    create_attribute,
    create_attribute_allowable_value_in_any_category,
    create_bq_batch16_qa_complete,
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
from src.csv_ingestion.uow.universal_attribute_values import (
    create_attribute_allowable_value_applicable_in_every_category,
)

GloballyAllowedValueRecord = (
    RawAttributeAllowableValueApplicableInEveryCategoryRecord
)
create_globally_allowed = (
    create_attribute_allowable_value_applicable_in_every_category
)


# NOTE: Ingestion takes a very long time if the
# ProductAttributeAllowableValue.csv is included.
# It is much more efficient for our purposes to skip over it.
# This is because the ProductAttributeAllowableValue.csv
# is a very large file and it takes a very long time to ingest.
# We can skip over it by not including it in the FILE_CONFIGS.


class CSVConfig:
    """Configuration for file processing"""

    FILE_CONFIGS = {
        "Product": {
            "model": RawProductRecord,
            "create_func": create_product,
            "column_mapping": {
                "ProductKey": "product_key",
                "SystemName": "system_name",
                "FriendlyName": "friendly_name",
            },
        },
        "Category": {
            "model": RawCategoryRecord,
            "create_func": create_category,
            "column_mapping": {
                "CategoryKey": "category_key",
                "SystemName": "system_name",
                "FriendlyName": "friendly_name",
            },
        },
        "Attribute": {
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
        "ProductCategory": {
            "model": RawProductCategoryRecord,
            "create_func": create_product_category,
            "column_mapping": {
                "ProductKey": "product_key",
                "CategoryKey": "category_key",
            },
        },
        "CategoryAttribute": {
            "model": RawCategoryAttributeRecord,
            "create_func": create_category_attribute,
            "column_mapping": {
                "CategoryAttributeKey": "category_attribute_key",
                "CategoryKey": "category_key",
                "AttributeKey": "attribute_key",
            },
        },
        "ProductAttributeValue": {
            "model": RawProductAttributeValueRecord,
            "create_func": create_product_attribute_value,
            "column_mapping": {
                "ProductKey": "product_key",
                "AttributeKey": "attribute_key",
                "Value": "value",
            },
        },
        "ProductAttributeGaps": {
            "model": RawProductAttributeGapRecord,
            "create_func": create_product_attribute_gap,
            "column_mapping": {
                "ProductKey": "product_key",
                "AttributeKey": "attribute_key",
            },
        },
        "ProductAttributeAllowableValue": {
            "model": RawProductAttributeAllowableValueRecord,
            "create_func": create_product_attribute_allowable_value,
            "column_mapping": {
                "ProductKey": "product_key",
                "AttributeKey": "attribute_key",
                "Value": "value",
            },
        },
        "CategoryAllowableValue": {
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
        "Recommendation": {
            "model": RawRecommendationRecord,
            "create_func": create_recommendation,
            "column_mapping": {
                "ProductKey": "product_key",
                "AttributeKey": "attribute_key",
                "RecommendedValue": "value",
                "ConfidenceScore": "confidence",
            },
        },
        "RichTextSource": {
            "model": RawRichTextSourceRecord,
            "create_func": create_rich_text_source,
            "column_mapping": {
                "ProductKey": "product_key",
                "RichText": "content",
                "RichTextName": "name",
                "RichTextPriority": "priority",
            },
        },
        "AttributeAllowableValuesApplicableInEveryCategory": {
            "model": GloballyAllowedValueRecord,
            "create_func": create_globally_allowed,
            "column_mapping": {
                "AttributeKey": "attribute_key",
                "AllowableValue": "value",
            },
        },
        "AttributeAllowableValueInAnyCategory": {
            "model": RawAttributeAllowableValueInAnyCategoryRecord,
            "create_func": create_attribute_allowable_value_in_any_category,
            "column_mapping": {
                "AttributeKey": "attribute_key",
                "Value": "value",
            },
        },
        "Output QA file for B&Q Batch 16 - B&Q QA Complete": {
            "model": HumanRecommendationRecord,
            "create_func": create_bq_batch16_qa_complete,
            "column_mapping": {
                "Product Reference": "product_reference",
                "Attribute Reference": "attribute_reference",
                "Attribute Name": "attribute_name",
                "Recommendation": "recommendation",
                "Unit": "unit",
                "Override": "override",
                "Alternative Override": "alternative_override",
                "Action": "action",
                "Link to site": "link_to_site",
                "Comment": "comment",
            },
        },
    }
