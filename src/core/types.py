from dataclasses import dataclass


@dataclass
class ProductAttributeValue:
    """Complete product information including all related data"""

    attribute: str
    value: str


@dataclass
class ProductDescriptor:
    """Complete product information including all related data"""

    descriptor: str
    value: str


@dataclass
class ProductAttributeGap:
    """Information about a missing attribute value and its possible values"""

    attribute: str
    allowable_values: list[str]
