from enum import Enum
import re


class ProductCodeType(str, Enum):
    """Valid product code types."""
    EAN = "EAN"
    UPC = "UPC"
    ISBN = "ISBN"
    SKU = "SKU"
    OTHER = "OTHER"

    @classmethod
    def validate_code_type(cls, code_type: str) -> "ProductCodeType":
        """
        Validate that a code type string matches one of the enum values.
        Raises ValueError with helpful message if invalid.
        """
        try:
            return cls(code_type)
        except ValueError:
            valid_types = ", ".join(t.value for t in cls)
            raise ValueError(
                f"Invalid code type: {code_type}. "
                f"Valid types are: {valid_types}"
            )

    @classmethod
    def detect_code_type(cls, code: str) -> "ProductCodeType":
        """
        Detect the type of product code based on its format.
        Defaults to EAN if no specific pattern is matched.
        """
        # Remove any non-alphanumeric characters
        code = re.sub(r'[^a-zA-Z0-9]', '', code)
        
        # EAN-13: 13 digits
        if re.match(r'^\d{13}$', code):
            return cls.EAN
        # EAN-8: 8 digits
        elif re.match(r'^\d{8}$', code):
            return cls.EAN
        # UPC-A: 12 digits
        elif re.match(r'^\d{12}$', code):
            return cls.UPC
        # ISBN-13: 13 digits starting with 978 or 979
        elif re.match(r'^(978|979)\d{10}$', code):
            return cls.ISBN
        # ISBN-10: 10 digits or 9 digits + X
        elif re.match(r'^\d{9}[\dX]$', code):
            return cls.ISBN
        # SKU: Typically alphanumeric with specific patterns
        elif re.match(r'^[A-Z0-9]{6,12}$', code):
            return cls.SKU
        else:
            return cls.OTHER


def process_code_type(system_name: str, code_type: str | None = None) -> str:
    """
    Process a product code to determine its type.
    If code_type is provided, validates it against allowed values.
    Otherwise, detects the type from the system_name.
    
    Args:
        system_name: The product code to process
        code_type: Optional explicit code type to use
        
    Returns:
        The code type as a string
    """
    if code_type is not None:
        return ProductCodeType.validate_code_type(code_type).value
    return ProductCodeType.detect_code_type(system_name).value 