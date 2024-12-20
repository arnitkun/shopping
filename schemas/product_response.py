from decimal import Decimal

from bson import Decimal128
from pydantic import BaseModel, Field

class ProductResponseSchema(BaseModel):
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=500)
    price: Decimal = Field(..., gt=0)
    stock: int = Field(..., gt=0)
    id: str
