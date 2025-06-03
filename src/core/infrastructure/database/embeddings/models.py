from datetime import datetime

from pydantic import BaseModel


class ProductEmbedding(BaseModel):
    """Represents a product embedding in the database"""

    product_key: str
    product_description: str
    embedding: list[float]
    created_at: datetime
    updated_at: datetime
