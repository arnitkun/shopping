from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from db.base_collection import MongoRepository


class DB:
    def __init__(self, mongo_url: str, db_name: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]


    def close(self):
        self.client.close()
        logger.info("MongoDB connection closed")

    @property
    def products(self):
        return self._get_repository("products")

    @property
    def orders(self):
        return self._get_repository("orders")

    @property
    def order_products(self):
        return self._get_repository("order_products")

    def _get_repository(self, collection_name: str):
        return MongoRepository(self.db, collection_name)

    async def setup_indexes(self):
        try:
            await self.db["products"].create_index(
                [("name", 1)],
                unique=True,
                name="unique_name_index"
            )
            logger.info("Unique index on 'products.name' created successfully.")
        except Exception as e:
            logger.error(f"Failed to create index on 'products.name': {e}")
