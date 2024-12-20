from typing import List

from pydantic import BaseModel

from schemas.order_product import OrderProductSchema


class OrderSchema(BaseModel):
    products: List[OrderProductSchema]