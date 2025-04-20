import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('x.env')

ATLAS_URI = os.getenv('ATLAS_URI')
DB_NAME = os.getenv('DB_NAME', 'home_monitor')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'sensor_readings')

# Initialize MongoDB client
client = MongoClient(ATLAS_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def insert_metric(data: dict) -> str:
    """
    Insert a sensor metric into the collection.
    
    Args:
        data: A dict containing sensor data (e.g., 'sensor_id', 'location', 'temperature', 'humidity').
    Returns:
        The inserted document's ID as a string.
    """
    doc = data.copy()
    # Ensure timestamp is present
    if 'timestamp' not in doc:
        doc['timestamp'] = datetime.utcnow()
    result = collection.insert_one(doc)
    return str(result.inserted_id)

def get_latest() -> dict:
    """
    Retrieve the most recent sensor metric document.
    
    Returns:
        The latest document or None if the collection is empty.
    """
    return collection.find_one(sort=[('timestamp', -1)])

def query_metrics(from_ts: datetime = None, to_ts: datetime = None) -> list:
    """
    Query sensor metrics between two timestamps.
    
    Args:
        from_ts: Inclusive lower bound as a datetime.
        to_ts: Inclusive upper bound as a datetime.
    Returns:
        List of matching documents sorted by timestamp descending.
    """
    query = {}
    if from_ts or to_ts:
        query['timestamp'] = {}
        if from_ts:
            query['timestamp']['$gte'] = from_ts
        if to_ts:
            query['timestamp']['$lte'] = to_ts
    cursor = collection.find(query).sort('timestamp', -1)
    return list(cursor)

if __name__ == '__main__':
    # Quick sanity check when running this file directly
    print("Inserting sample metric...")
    sample_id = insert_metric({
        'sensor_id': 'test-sensor',
        'location': 'living_room',
        'temperature': 22.5,
        'humidity': 50.0
    })
    print("Inserted ID:", sample_id)
    print("Latest metric:", get_latest())
