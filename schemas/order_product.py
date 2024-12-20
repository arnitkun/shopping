from pydantic import BaseModel, Field

class OrderProductSchema(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)