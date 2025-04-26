from collections.abc import Iterable

from bson import ObjectId
from pymongo import MongoClient
from re import escape, compile, IGNORECASE


class Database:
    def __init__(self, host: str, port: int, name: str):
        self.client = MongoClient(f'mongodb://{host}:{port}')
        self.db = self.client[name]

    def insert(self, collection_name: str, data: list[dict]):
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

    def remove_one(self, collection_name: str, id: str):
        filter = {'_id': ObjectId(id), 'quantity': {'$gt': 0}}
        update = {'$inc': {'quantity': -1}}
        price = self.db[collection_name].find_one(filter)['price']
        update_result = self.db[collection_name].update_one(filter, update)
        return update_result.matched_count * price
