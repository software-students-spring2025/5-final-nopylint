import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('x.env')

ATLAS_URI = os.getenv('ATLAS_URI')
MONGO_URI = os.getenv('MONGO_URI') or os.getenv('ATLAS_URI', 'mongodb://localhost:27017')
# DB_NAME = os.getenv('DB_NAME', 'home_monitor')
# COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'sensor_readings')

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

# TEST
# if __name__ == '__main__':
#     print("Inserting sample metric...")
#     sample_id = insert_metric({
#         'sensor_id': 'test-sensor',
#         'location': 'living_room',
#         'temperature': 22.5,
#         'humidity': 50.0
#     })
#     print("Inserted ID:", sample_id)
#     print("Latest metric:", get_latest())
