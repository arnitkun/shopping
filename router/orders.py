
from bson import ObjectId
from fastapi import Depends, APIRouter, HTTPException

from db.db import DB
from main import get_db
from schemas.order import OrderSchema

orders_router = APIRouter()

@orders_router.post("/orders", response_model=dict)
async def place_order(order: OrderSchema, db: DB = Depends(get_db)):
    try:
        total_price = 0
        order_items = []

        session = await db.client.start_session()

        async with session.start_transaction():
            for item in order.products:
                product = await db.products.find_one({"_id": ObjectId(item.product_id)})

                if not product:
                    raise HTTPException(status_code=404, detail=f"Product with id: {item.product_id} not found.")

                if product["stock"] < item.quantity:
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product['name']}.")

                await db.products.update_one(
                    {"_id": ObjectId(item.product_id)},
                    {"$inc": {"stock": -item.quantity}},
                    session=session
                )

                total_price += product["price"] * item.quantity
                order_items.append({"product_id": ObjectId(item.product_id), "quantity": item.quantity})

            new_order = {"products": order_items, "total_price": total_price, "status": "pending"}
            order_id = await db.orders.insert_one(new_order, session=session)

        return {"message": "Order placed successfully!", "order_id": str(order_id)}
    except Exception as e:
        raise e