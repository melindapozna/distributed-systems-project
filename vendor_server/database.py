from collections.abc import Iterable

from bson.objectid import ObjectId
from pymongo import MongoClient
from re import escape, compile, IGNORECASE


class Database:
    def __init__(self, host: str, port: int, name: str):
        self.client = MongoClient(f'mongodb://{host}:{port}')
        #self.client = MongoClient(f'mongodb://{user}:{password}@{host}:27017/{name}?authSource=admin')
        #^^db particularities on my end, ignore this
        self.db = self.client[name]

    def insert(self, collection_name: str, data: list[dict]):
        for entry in data:
            if 'price' in entry and entry['price'] < 0:
                raise ValueError(f'Price cannot be negative: {entry}')
            if 'quantity' in entry and entry['quantity'] < 0:
                raise ValueError(f'Quantity cannot be negative: {entry}')
        self.db[collection_name].insert_many(data)

    def select(self, collection_name: str) -> Iterable:
        return self.db[collection_name].find()

    def search(self, collection_name: str, query: str, fields: list[str]) -> Iterable:
        db_search_query = {}
        # Escaping the query string to safely use it in a regular expression
        search_string = compile(escape(query.strip()), flags=IGNORECASE)
        for field in fields:
            db_search_query[field] = {'$regex': search_string}

        return self.db[collection_name].find(db_search_query)

    def remove_one(self, collection_name: str, id: str) -> int | None:
        filter = {'_id': ObjectId(id), 'quantity': {'$gt': 0}}
        update = {'$inc': {'quantity': -1}}
        item = self.db[collection_name].find_one({'_id': ObjectId(id)})
        if not item:
            raise KeyError(f'No item found with id {id}')
        price = item['price']
        update_result = self.db[collection_name].update_one(filter, update)
        print(update_result)
        if update_result.matched_count == 0:
            return None
        return price

    def drop_collection(self, collection_name: str):
        self.db[collection_name].drop()
