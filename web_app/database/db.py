import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('x.env')
USE_MOCK_DB = os.getenv('USE_MOCK_DB', 'false').lower() == 'true'
if USE_MOCK_DB:
    from mongomock import MongoClient
else:
    from pymongo import MongoClient

MONGO_URI = os.getenv('MONGO_URI') or os.getenv('ATLAS_URI', 'mongodb://localhost:27017')

DB_NAME = os.getenv('DB_NAME', 'app_testing')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'api_records')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def insert_metric(data: dict) -> str:
    doc = data.copy()
    if 'timestamp' not in doc:
        doc['timestamp'] = datetime.utcnow()
    result = collection.insert_one(doc)
    return str(result.inserted_id)

def get_latest() -> dict:
    return collection.find_one(sort=[('timestamp', -1)])

def query_metrics(from_ts: datetime = None, to_ts: datetime = None) -> list:
    query = {}
    if from_ts or to_ts:
        query['timestamp'] = {}
        if from_ts:
            query['timestamp']['$gte'] = from_ts
        if to_ts:
            query['timestamp']['$lte'] = to_ts
    cursor = collection.find(query).sort('timestamp', -1)
    return list(cursor)
