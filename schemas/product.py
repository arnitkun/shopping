from decimal import Decimal

from bson import Decimal128
from pydantic import BaseModel, Field

class ProductSchema(BaseModel):
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=500)
    price: Decimal = Field(..., gt=0)
    stock: int = Field(..., gt=0)

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data['price'] = Decimal128(data['price'])
        return data
