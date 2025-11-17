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

# Global wait time (in minutes) - placeholder for delay tracking
GLOBAL_WAIT_TIME_MINUTES = 15


# default route
@app.route("/", methods=["GET"])
def root_service():
    return json.dumps({"msg": "UrgentCareQ Backend", "port": PORT}), 200, {"Content-Type": "application/json"}




# -----------------------------------------------------------
# staff endpoints
# -----------------------------------------------------------



# staff/queue: get current queue
@app.get("/api/staff/queue")
def staff_get_queue():
    # mongo uri check
    if queue_collection is None:
        return json.dumps({"error": "MONGODB_URI not set"}), 500, {"Content-Type": "application/json"}

    qdoc = queue_collection.find_one({"queue_id": "main"}) or queue_collection.find_one({})
    if qdoc is None:
        return json.dumps({"error": "queue not initialized", "patients": []}), 200, {"Content-Type": "application/json"}

    patients = qdoc.get("patients", [])
    
    # Format patient data for frontend
    formatted_patients = []
    for i, patient in enumerate(patients):
        formatted_patients.append({
            "position": i,
            "name": patient.get("name", "Unknown"),
            "phone": patient.get("phone", "N/A"),
            "dob": patient.get("dob", "N/A"),
            "symptoms": patient.get("symptoms", "N/A"),
            "status": patient.get("status", "waiting"),
            "checked_in": patient.get("checked_in", False),
            "scheduled_time": patient.get("scheduled_time").isoformat() if patient.get("scheduled_time") else "N/A"
        })
    
    return json.dumps({
        "queue_id": qdoc.get("queue_id", "main"),
        "start_time": qdoc.get("start_time").isoformat() if qdoc.get("start_time") else None,
        "slot_seconds": qdoc.get("slot_seconds", 900),
        "patients": formatted_patients,
        "total_patients": len(formatted_patients),
        "global_wait_time_minutes": GLOBAL_WAIT_TIME_MINUTES
    }), 200, {"Content-Type": "application/json"}

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


# staff/queue: get entire queue with all patients
@app.route("/api/staff/queue", methods=["GET"])
def staff_get_queue():
    if queue_collection is None:
        return json.dumps({"error": "MONGODB_URI not set"}), 500, {"Content-Type": "application/json"}

    qdoc = queue_collection.find_one({"queue_id": "main"}) or queue_collection.find_one({})
    if qdoc is None:
        return json.dumps({"error": "queue not initialized"}), 400, {"Content-Type": "application/json"}

    patients = qdoc.get("patients", [])
    patients_with_position = []
    i = 0
    for p in patients:
        patient_data = dict(p)
        # ensure datetime fields are isoformatted
        sc = patient_data.get("scheduled_time")
        if isinstance(sc, datetime):
            patient_data["scheduled_time"] = sc.isoformat()
        patient_data["position"] = i
        patients_with_position.append(patient_data)
        i += 1

    return json.dumps({
        "queue_id": qdoc.get("queue_id", "main"),
        "start_time": qdoc.get("start_time").isoformat(),
        "slot_seconds": qdoc.get("slot_seconds", 900),
        "total_patients": len(patients),
        "created_at": qdoc.get("created_at").isoformat(),
        "patients": patients_with_position
    }), 200, {"Content-Type": "application/json"}


# staff/search: search patients by name
@app.route("/api/staff/search", methods=["GET"])
def staff_search():
    if queue_collection is None:
        return json.dumps({"error": "MONGODB_URI not set"}), 500, {"Content-Type": "application/json"}

    qdoc = queue_collection.find_one({"queue_id": "main"}) or queue_collection.find_one({})
    if qdoc is None:
        return json.dumps({"error": "queue not initialized"}), 400, {"Content-Type": "application/json"}

    search_name = (request.args.get("name") or "").strip()
    if not search_name:
        return json.dumps({"patients": []}), 200, {"Content-Type": "application/json"}

    patients = qdoc.get("patients", [])
    matches = []
    i = 0
    for p in patients:
        if search_name.lower() in p.get("name", "").lower():
            patient_data = dict(p)
            sc = patient_data.get("scheduled_time")
            if isinstance(sc, datetime):
                patient_data["scheduled_time"] = sc.isoformat()
            patient_data["position"] = i
            matches.append(patient_data)
        i += 1

    return json.dumps({"patients": matches}), 200, {"Content-Type": "application/json"}


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
        "scheduled_time": scheduled_dt,
        "status": "waiting",
        "checked_in": False,
        "checked_in_at": None,
        "admitted_at": None,
        "completed_at": None,
        "actual_duration_minutes": None
    }

    queue_collection.update_one({"_id": qdoc["_id"]}, {"$push": {"patients": patient}})

    # Calculate wait time including global delay
    base_wait_minutes = (position * slot_seconds) // 60
    total_wait_minutes = base_wait_minutes + GLOBAL_WAIT_TIME_MINUTES

    return json.dumps({
        "position": position,
        "scheduled_time": scheduled_dt.isoformat(),
        "estimated_wait_minutes": base_wait_minutes,
        "total_wait_minutes": total_wait_minutes,
        "global_delay_minutes": GLOBAL_WAIT_TIME_MINUTES
    }), 200, {"Content-Type": "application/json"}


# patient/checkin: marks a patient as checked in
@app.post("/api/patient/checkin")
def patient_checkin():
    # mongo uri check
    if queue_collection is None:
        return json.dumps({"error": "MONGODB_URI not set"}), 500, {"Content-Type": "application/json"}

    name = (request.form.get("patient_name") or "").strip()
    dob = (request.form.get("dob") or "").strip()
    
    if not name:
        return json.dumps({"error": "Patient name is required"}), 400, {"Content-Type": "application/json"}

    # Find queue
    qdoc = queue_collection.find_one({"queue_id": "main"}) or queue_collection.find_one({})
    if qdoc is None:
        return json.dumps({"error": "queue not initialized"}), 400, {"Content-Type": "application/json"}

    # Find patient in the queue by name (and optionally DOB for disambiguation)
    patients = qdoc.get("patients", [])
    matching_patients = []
    
    for i, patient in enumerate(patients):
        if patient.get("name", "").strip().lower() == name.lower():
            matching_patients.append((i, patient))
    
    if not matching_patients:
        return json.dumps({"error": f"Patient '{name}' not found in queue"}), 404, {"Content-Type": "application/json"}
    
    # If multiple patients with same name, use DOB to disambiguate
    if len(matching_patients) > 1:
        if not dob:
            return json.dumps({
                "error": f"Multiple patients named '{name}' found. Please provide date of birth.",
                "requires_dob": True
            }), 400, {"Content-Type": "application/json"}
        
        # Filter by DOB
        matching_patients = [(i, p) for i, p in matching_patients if p.get("dob") == dob]
        
        if not matching_patients:
            return json.dumps({"error": f"No patient '{name}' with DOB {dob} found"}), 404, {"Content-Type": "application/json"}
    
    # Mark patient as checked in
    idx, patient = matching_patients[0]
    patients[idx]["checked_in"] = True
    patients[idx]["checked_in_at"] = datetime.now()
    patients[idx]["status"] = "checked_in"
    scheduled_time = patient.get("scheduled_time")
    
    # Update the queue with the modified patients array
    queue_collection.update_one(
        {"_id": qdoc["_id"]},
        {"$set": {"patients": patients}}
    )

    return json.dumps({
        "message": "Check-in successful",
        "patient_name": name,
        "checked_in": True,
        "scheduled_time": scheduled_time.isoformat() if scheduled_time else None
    }), 200, {"Content-Type": "application/json"}


# staff/admit: mark patient as admitted (started)
@app.post("/api/staff/admit")
def staff_admit():
    # mongo uri check
    if queue_collection is None:
        return json.dumps({"error": "MONGODB_URI not set"}), 500, {"Content-Type": "application/json"}

    name = (request.form.get("patient_name") or "").strip()
    if not name:
        return json.dumps({"error": "Patient name is required"}), 400, {"Content-Type": "application/json"}

    # Find queue
    qdoc = queue_collection.find_one({"queue_id": "main"}) or queue_collection.find_one({})
    if qdoc is None:
        return json.dumps({"error": "queue not initialized"}), 400, {"Content-Type": "application/json"}

    # Find patient in the queue by name
    patients = qdoc.get("patients", [])
    patient_found = False
    
    for i, patient in enumerate(patients):
        if patient.get("name", "").strip().lower() == name.lower():
            # Check if patient is checked in
            if not patient.get("checked_in"):
                return json.dumps({"error": "Patient must be checked in before being admitted"}), 400, {"Content-Type": "application/json"}
            
            # Mark as admitted
            patients[i]["status"] = "admitted"
            patients[i]["admitted_at"] = datetime.now()
            patient_found = True
            break
    
    if not patient_found:
        return json.dumps({"error": f"Patient '{name}' not found in queue"}), 404, {"Content-Type": "application/json"}
    
    # Update the queue
    queue_collection.update_one(
        {"_id": qdoc["_id"]},
        {"$set": {"patients": patients}}
    )

    return json.dumps({
        "message": "Patient admitted successfully",
        "patient_name": name,
        "status": "admitted"
    }), 200, {"Content-Type": "application/json"}


# staff/checkout: mark patient as completed, remove from queue, and calculate duration
@app.post("/api/staff/checkout")
def staff_checkout():
    # mongo uri check
    if queue_collection is None:
        return json.dumps({"error": "MONGODB_URI not set"}), 500, {"Content-Type": "application/json"}

    name = (request.form.get("patient_name") or "").strip()
    if not name:
        return json.dumps({"error": "Patient name is required"}), 400, {"Content-Type": "application/json"}

    # Find queue
    qdoc = queue_collection.find_one({"queue_id": "main"}) or queue_collection.find_one({})
    if qdoc is None:
        return json.dumps({"error": "queue not initialized"}), 400, {"Content-Type": "application/json"}

    # Find patient in the queue by name
    patients = qdoc.get("patients", [])
    patient_found = False
    patient_to_remove = None
    
    for i, patient in enumerate(patients):
        if patient.get("name", "").strip().lower() == name.lower():
            # Check if patient is admitted
            if patient.get("status") != "admitted":
                return json.dumps({"error": "Patient must be admitted before checkout"}), 400, {"Content-Type": "application/json"}
            
            # Calculate duration
            admitted_at = patient.get("admitted_at")
            completed_at = datetime.now()
            
            if admitted_at:
                duration = (completed_at - admitted_at).total_seconds() / 60
                patient["actual_duration_minutes"] = round(duration, 2)
            else:
                patient["actual_duration_minutes"] = 0
            
            patient["completed_at"] = completed_at
            patient["status"] = "completed"
            
            patient_to_remove = i
            patient_found = True
            break
    
    if not patient_found:
        return json.dumps({"error": f"Patient '{name}' not found in queue"}), 404, {"Content-Type": "application/json"}
    
    # Remove patient from queue
    removed_patient = patients.pop(patient_to_remove)
    
    # Update the queue
    queue_collection.update_one(
        {"_id": qdoc["_id"]},
        {"$set": {"patients": patients}}
    )

    return json.dumps({
        "message": "Patient checked out successfully",
        "patient_name": name,
        "status": "completed",
        "actual_duration_minutes": removed_patient.get("actual_duration_minutes"),
        "admitted_at": removed_patient.get("admitted_at").isoformat() if removed_patient.get("admitted_at") else None,
        "completed_at": removed_patient.get("completed_at").isoformat() if removed_patient.get("completed_at") else None
    }), 200, {"Content-Type": "application/json"}


# patient/getstatus: get patient's queue status
@app.route("/api/patient/getstatus", methods=["GET"])
def patient_getstatus():
    if queue_collection is None:
        return json.dumps({"error": "MONGODB_URI not set"}), 500, {"Content-Type": "application/json"}

    qdoc = queue_collection.find_one({"queue_id": "main"}) or queue_collection.find_one({})
    if qdoc is None:
        return json.dumps({"error": "queue not initialized"}), 400, {"Content-Type": "application/json"}

    name = (request.args.get("patient_name") or "").strip()
    phone = request.args.get("phone") or ""
    if not name or not phone:
        return json.dumps({"error": "patient_name and phone required"}), 400, {"Content-Type": "application/json"}

    patients = qdoc.get("patients", [])
    patient = None
    position = None
    i = 0
    for p in patients:
        if p.get("name", "").strip() == name and p.get("phone", "") == phone:
            patient = p
            position = i
            break
        i += 1

    if patient is None:
        return json.dumps({"error": "patient not found"}), 404, {"Content-Type": "application/json"}

    slot_seconds = int(qdoc.get("slot_seconds", 900))
    scheduled_dt = patient.get("scheduled_time")
    now = datetime.now()
    wait_seconds = max(0, (scheduled_dt - now).total_seconds())
    wait_minutes = int(wait_seconds // 60)

    return json.dumps({
        "name": patient.get("name"),
        "phone": patient.get("phone"),
        "position": position,
        "scheduled_time": scheduled_dt.isoformat(),
        "estimated_wait_minutes": wait_minutes,
        "checked_in": patient.get("checked_in", False)
    }), 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    # Debug: print registered routes and file path to ensure correct server is running
    try:
        print("Loaded server from:", __file__)
        print("Registered routes:",[r.rule for r in app.url_map.iter_rules()])
    except Exception:
        pass
    app.run(host="127.0.0.1", port=PORT)


