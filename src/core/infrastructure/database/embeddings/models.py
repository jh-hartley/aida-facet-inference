from datetime import datetime

from pydantic import BaseModel


class ProductEmbedding(BaseModel):
    """Represents a product embedding in the database"""

    product_key: str
    embedding: list[float]
    created_at: datetime
