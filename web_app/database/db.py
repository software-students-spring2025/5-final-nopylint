import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv('x.env')
USE_MOCK_DB = os.getenv('USE_MOCK_DB', 'false').lower() == 'true'
if USE_MOCK_DB:
    from mongomock import MongoClient
else:
    from pymongo import MongoClient

MONGO_URI = os.getenv('MONGO_URI') or os.getenv('ATLAS_URI')

DB_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')
HISTORY=os.getenv('HISTORY')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
history=db[HISTORY]

def insert_metric(data: dict) -> str:
    doc = data.copy()
    if 'timestamp' not in doc:
        doc['timestamp'] = datetime.now(timezone.utc)
    result = collection.insert_one(doc)
    return str(result.inserted_id)

def save(data: dict) -> str:
    doc = data.copy()
    if 'timestamp' not in doc:
        doc['timestamp'] = datetime.now(timezone.utc)
    result = history.insert_one(doc)
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

def fetch_history(from_ts: datetime = None, to_ts: datetime = None) -> list:
    query = {}
    if from_ts or to_ts:
        query['timestamp'] = {}
        if from_ts:
            query['timestamp']['$gte'] = from_ts
        if to_ts:
            query['timestamp']['$lte'] = to_ts
    cursor = history.find(query).sort('timestamp', -1)
    return list(cursor)
