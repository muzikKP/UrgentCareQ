from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))
from q_system import PatientQueue
from datetime import datetime

# Load env from backend/.env
_env_dir = Path(__file__).resolve().parent
_env_path = _env_dir / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    _envfile = _env_dir / "envfile.txt"
    if _envfile.exists():
        load_dotenv(dotenv_path=_envfile)

uri = os.environ.get("MONGODB_URI")
if not uri:
    raise SystemExit("MONGODB_URI not set. Add it to backend/.env or backend/envfile.txt")


client = MongoClient(uri, server_api=ServerApi('1'))
# ping DB to confirm a successful connection
try:
    client.admin.command('ping')
    print("Connected to MongoDB")
except Exception as e:
    print(e)

# Initialize new queue
db = client.urgentcare
queue_collection = db.queue

# Clear existing queue and create new one
queue_collection.delete_many({})
pq = PatientQueue(slot_seconds=900, start_time=datetime.now())
queue_collection.insert_one({
    "queue_id": "main",
    "start_time": pq.start_time,
    "slot_seconds": pq.slot_seconds,
    "patients": [],
    "created_at": datetime.now()
})
print("Queue initialized")