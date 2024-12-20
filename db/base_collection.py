from decimal import Decimal

from bson import Decimal128


class MongoRepository:
    def __init__(self, db, collection_name: str):
        self.collection = db[collection_name]
        self.decimal_prc = Decimal(f"1e-2")

    def shouldConvertToDecimal128(self, val):
        is_decimal = isinstance(val, Decimal)
        return is_decimal

    def cast_to_decimal(self, value):
        if isinstance(value, Decimal128):
            value = value.to_decimal()
        return Decimal(value).quantize(self.decimal_prc)

    async def find(self, query):
        cursor = self.collection.find(query)
        res = await self.convert_decimal128_to_decimal(cursor)
        return res

    async def find_one(self, query):
        result = await self.collection.find_one(query)
        if result:
            if isinstance(result.get('price'), Decimal128):
                result['price'] = self.cast_to_decimal(result['price'])
                return result
        return None

    async def insert_one(self, document, session=None):

        for k in document.keys():
            if self.shouldConvertToDecimal128(document[k]):
                document[k] = Decimal128((document[k]))
        result = await self.collection.insert_one(document, session=session)
        return result.inserted_id

    async def update_one(self, query, update, session=None):
        if '$set' in update:
            for key, value in update['$set'].items():
                if isinstance(value, Decimal):
                    update['$set'][key] = Decimal128(value)
        await self.collection.update_one(query, update, session=session)

    async def convert_decimal128_to_decimal(self, cursor):
        converted_results = []
        async for document in cursor:
            if isinstance(document.get('price'), Decimal128):
                document['price'] = self.cast_to_decimal(document['price'])
            if isinstance(document.get('total_price'), Decimal128):
                document['total_price'] = self.cast_to_decimal(document['total_price'])
            converted_results.append(document)
        return converted_results
