from collections.abc import Iterable
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
        search_string = compile(escape(query), flags=IGNORECASE)
        for field in fields:
            db_search_query[field] = {'$regex': search_string}

        return self.db[collection_name].find(db_search_query)

