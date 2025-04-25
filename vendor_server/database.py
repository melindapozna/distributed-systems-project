from pymongo import MongoClient


class Database:
    def __init__(self, host, port):
        self.client = MongoClient(f'mongodb://{host}:{port}')

    def insert(self, db_name, collection_name, data):
        self.client[db_name][collection_name].insert_many(data)

    def select(self, db_name, collection_name):
        return self.client[db_name][collection_name].find()