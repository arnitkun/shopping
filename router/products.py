from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pymongo.errors import DuplicateKeyError

from db.db import DB
from main import get_db
from schemas.product import ProductSchema
from schemas.product_response import ProductResponseSchema

product_router = APIRouter()

@product_router.get("/products", response_model=List[ProductResponseSchema])
async def get_products(db: DB = Depends(get_db)):
    products = await db.products.find({})
    for product in products:
        product["id"] = str(product["_id"])
    return products

@product_router.post("/products", response_model=dict)
async def add_product(product: ProductSchema, db: DB = Depends(get_db)):
    try:
        product_dict = product.model_dump()
        product_id = await db.products.insert_one(product_dict)
        return {"message": "Product added successfully!", "id": str(product_id)}
    except DuplicateKeyError as de:
        logger.error(f"Failed to insert into 'products': {de}, product already exists.")
        raise HTTPException(status_code=400, detail=f"Failed to insert into 'products', product already exists.")
    except Exception as e:
        logger.error(f"Failed to insert into 'products': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to insert into 'products': {e}")
