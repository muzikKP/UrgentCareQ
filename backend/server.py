"""
Filename: server.py
Author: John Anthony Kadian
Created: 2025-10-10
Description: Minimal Flask backend for UrgentCareQ
"""

from flask import Flask, request
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta

PORT: int = 5001

app = Flask(__name__)

# Mongo client setup
_env_dir = Path(__file__).resolve().parent
_env_path = _env_dir / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    _envfile = _env_dir / "envfile.txt"
    if _envfile.exists():
        load_dotenv(dotenv_path=_envfile)

uri = os.environ.get("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1')) if uri else None
db = client.urgentcare if client is not None else None
queue_collection = db.queue if db is not None else None


# default route
@app.get("/")
def root_service():
    return json.dumps({"msg": "UrgentCareQ Backend", "port": PORT}), 200, {"Content-Type": "application/json"}




# -----------------------------------------------------------
# staff endpoints
# -----------------------------------------------------------



# staff/reset: reset the queue (delete existing queue if one, and create a new one in its place)
@app.post("/api/staff/reset")
def staff_reset():
    # mongo uri check
    if queue_collection is None:
        return json.dumps({"error": "MONGODB_URI not set"}), 500, {"Content-Type": "application/json"}

    queue_collection.delete_many({})
    now = datetime.now()
    doc = {
        "queue_id": "main",
        "start_time": now,
        "slot_seconds": 900,
        "patients": [],
        "created_at": now
    }
    queue_collection.insert_one(doc)
    return json.dumps({"queue_id": "main", "start_time": now.isoformat(), "slot_seconds": 900}), 200, {"Content-Type": "application/json"}



# -----------------------------------------------------------
# patient endpoints
# -----------------------------------------------------------



# patient/joinqueue: adds patient to the queue 
@app.post("/api/patient/joinqueue")
def patient_joinqueue():
    # mongo uri check
    if queue_collection is None:
        return json.dumps({"error": "MONGODB_URI not set"}), 500, {"Content-Type": "application/json"}

    # ensure queue exists
    qdoc = queue_collection.find_one({"queue_id": "main"}) or queue_collection.find_one({})
    if qdoc is None:
        return json.dumps({"error": "queue not initialized"}), 400, {"Content-Type": "application/json"}

    name = (request.form.get("patient_name") or "").strip()
    phone = request.form.get("phone") or ""
    dob = request.form.get("dob") or ""
    insurance = request.form.get("insurance") or ""
    symptoms = request.form.get("symptoms") or ""

    patients = qdoc.get("patients", [])
    position = len(patients)
    slot_seconds = int(qdoc.get("slot_seconds", 900))
    start_time = qdoc.get("start_time")
    scheduled_dt = start_time + timedelta(seconds=position * slot_seconds)

    patient = {
        "name": name,
        "phone": phone,
        "dob": dob,
        "insurance": insurance,
        "symptoms": symptoms,
        "scheduled_time": scheduled_dt
    }

    queue_collection.update_one({"_id": qdoc["_id"]}, {"$push": {"patients": patient}})

    return json.dumps({
        "position": position,
        "scheduled_time": scheduled_dt.isoformat(),
        "estimated_wait_minutes": (position * slot_seconds) // 60
    }), 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT)


