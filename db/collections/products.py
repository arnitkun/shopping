from motor.motor_asyncio import AsyncIOMotorClient
from db import base_collection

class ProductRepository(base_collection):
    def __init__(self, mongo_url: str, db_name: str):
        db = AsyncIOMotorClient(mongo_url)[db_name]
        super().__init__(db, "products")
        self.create_indexes()

    def create_indexes(self):
        self.collection.create_index("name", unique=True)