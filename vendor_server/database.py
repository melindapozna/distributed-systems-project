from collections.abc import Iterable

from bson import ObjectId
from pymongo import MongoClient, ReturnDocument
from re import escape, compile, IGNORECASE
from typing import Optional, Tuple


class Database:
    def __init__(self, host: str, port: int, name: str):
        self.client = MongoClient(f'mongodb://{host}:{port}')
        self.db = self.client[name]

    def insert(self, collection_name: str, data: list[dict]):
        for entry in data:
            if 'price' in entry and entry['price'] < 0:
                raise ValueError(f'Price cannot be negative: {entry}')
            if 'quantity' in entry and entry['quantity'] < 0:
                raise ValueError(f'Quantity cannot be negative: {entry}')
        self.db[collection_name].insert_many(data)

    def search(self, collection_name: str, query: str, fields: list[str]) -> Iterable:
        db_search_query = {}
        # Escaping the query string to safely use it in a regular expression
        search_string = compile(escape(query.strip()), flags=IGNORECASE)
        for field in fields:
            db_search_query[field] = {'$regex': search_string}

        return self.db[collection_name].find(db_search_query)

    # Reduces the quantity of one item in the stock by a given number
    def remove_from_document(self, collection_name: str, id: str, quantity: int) -> Optional[Tuple[int, str]]:
        filter = {'_id': ObjectId(id), 'quantity': {'$gte': quantity}}
        update = {'$inc': {'quantity': -quantity}}
        update_result = self.db[collection_name].find_one_and_update(filter, update)

        if not update_result:
            return None
        return update_result['price']

    def remove_multiple_items(self, collection_name: str, entries: list[dict]) -> Optional[Tuple[int, int]]:
        total_price = 0
        update_count = 0
        # All items are purchased or the transaction is cancelled and nothing is purchased
        with self.client.start_session() as session:
            with session.start_transaction():
                for item in entries:
                    try:
                        id = item['id']
                        quantity = item['quantity']
                    except Exception as e:
                        # Malformed request
                        return None
                    if quantity <= 0:
                        update_count += 1
                        continue
                    filter = {'_id': ObjectId(id), 'quantity': {'$gte': quantity}}
                    update = {'$inc': {'quantity': -quantity}}
                    update_result = self.db[collection_name].find_one_and_update(filter, update, session=session)
                    # If nothing is updated this line crashes and stops the transaction
                    total_price += quantity * update_result['price']
                    update_count += 1

        return total_price, update_count


    def drop_collection(self, collection_name: str):
        self.db[collection_name].drop()
