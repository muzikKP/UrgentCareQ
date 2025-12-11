"""
Filename: server.py
Author: John Anthony Kadian
Contributers: Kush Parmar, Niranjan Vijay Badhe
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
import math
import threading
import time

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

# Buffer time to prep room, can be adjusted by staff
PREP_MINUTES = 10

# These are arbitrary estimates based on typical urgent care guidance
# in the future, these can be reassigned to estimates derived from data collected from the clinic
REASON_ESTIMATE_MINUTES = {
    "Flu-like symptoms": 20,
    "Minor laceration": 25,
    "COVID-19 test": 10,
    "Common infections (ear, pink eye)": 15,
    "Sore throat / strep check": 15,
    "Sprain/strain": 30,
    "Rash or allergic reaction (mild)": 15,
    "Urinary symptoms (possible UTI)": 20,
    "Medication refill/quick consult": 10,
}


# default route
@app.get("/")
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
            "reason": patient.get("reason", "N/A"),
            "status": patient.get("status", "waiting"),
            "checked_in": patient.get("checked_in", False),
            "scheduled_time": patient.get("scheduled_time").isoformat() if patient.get("scheduled_time") else "N/A",
            "expected_start_time": patient.get("expected_start_time").isoformat() if patient.get("expected_start_time") else None,
            "expected_end_time": patient.get("expected_end_time").isoformat() if patient.get("expected_end_time") else None,
            "expected_duration_minutes": patient.get("expected_duration_minutes"),
            "initial_wait_minutes": patient.get("initial_wait_minutes"),
            "checkin_deadline": patient.get("checkin_deadline").isoformat() if patient.get("checkin_deadline") else None,
            "admitted_at": patient.get("admitted_at").isoformat() if patient.get("admitted_at") else None,
            "completed_at": patient.get("completed_at").isoformat() if patient.get("completed_at") else None,
            "actual_duration_minutes": patient.get("actual_duration_minutes"),
        })

    return json.dumps({
        "queue_id": qdoc.get("queue_id", "main"),
        "start_time": qdoc.get("start_time").isoformat() if qdoc.get("start_time") else None,
        "room_free_at": qdoc.get("room_free_at").isoformat() if qdoc.get("room_free_at") else None,
        "global_delay_minutes": qdoc.get("global_delay_minutes", 0),
        "patients": formatted_patients,
        "total_patients": len(formatted_patients)
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
        "room_free_at": None,  # None means free now
        "global_delay_minutes": 0,
        "patients": [],
        "created_at": now
    }
    queue_collection.insert_one(doc)
    return json.dumps({
        "queue_id": "main",
        "start_time": now.isoformat(),
        "room_free_at": None,
        "global_delay_minutes": 0
    }), 200, {"Content-Type": "application/json"}



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
    reason = (request.form.get("reason") or "").strip()

    patients = qdoc.get("patients", [])
    position = len(patients)

    now = datetime.now()
    room_free_at = qdoc.get("room_free_at")
    effective_free_at = now if (room_free_at is None or room_free_at <= now) else room_free_at

    # Estimate expected duration
    reason_key = (reason or "").strip()
    estimated_reason_minutes = REASON_ESTIMATE_MINUTES.get(reason_key, 15)
    expected_duration_minutes = PREP_MINUTES + estimated_reason_minutes

    expected_start_time = effective_free_at
    expected_end_time = expected_start_time + timedelta(minutes=expected_duration_minutes)

    # Initial wait minutes for this patient
    wait_seconds = max(0, (effective_free_at - now).total_seconds())
    initial_wait_minutes = int(math.ceil(wait_seconds / 60.0)) if wait_seconds > 0 else 0

    # Set deadline 5 minutes prior to expected start
    # but not before 'now' to avoid conflicts with first patient check-in time requirements
    checkin_deadline = None
    # avoid conlicts with first patient check-in time requirements
    check_in_by_str = "ASAP" if position == 0 else None
    if position != 0:
        deadline = expected_start_time - timedelta(minutes=5)
        if deadline < now:
            deadline = now
        checkin_deadline = deadline
        check_in_by_str = deadline.isoformat()

    patient = {
        "name": name,
        "phone": phone,
        "dob": dob,
        "insurance": insurance,
        "reason": reason,
        "scheduled_time": expected_start_time,
        "expected_start_time": expected_start_time,
        "expected_end_time": expected_end_time,
        "expected_duration_minutes": expected_duration_minutes,
        "initial_wait_minutes": initial_wait_minutes,
        "checkin_deadline": checkin_deadline,
        "status": "waiting",
        "checked_in": False,
        "checked_in_at": None,
        "admitted_at": None,
        "completed_at": None,
        "actual_duration_minutes": None
    }

    # Add patient and advance room_free_at to expected_end_time
    queue_collection.update_one(
        {"_id": qdoc["_id"]},
        {
            "$push": {"patients": patient},
            "$set": {"room_free_at": expected_end_time}
        }
    )

    return json.dumps({
        "position": position,
        "scheduled_time": expected_start_time.isoformat(),
        "expected_start_time": expected_start_time.isoformat(),
        "expected_end_time": expected_end_time.isoformat(),
        "expected_duration_minutes": expected_duration_minutes,
        "initial_wait_minutes": initial_wait_minutes,
        "check_in_by": check_in_by_str
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

    # Find patient in the queue by name
    patients = qdoc.get("patients", [])
    matching_patients = []

    for i, patient in enumerate(patients):
        if patient.get("name", "").strip().lower() == name.lower():
            matching_patients.append((i, patient))

    if not matching_patients:
        return json.dumps({"error": f"Patient '{name}' not found in queue"}), 404, {"Content-Type": "application/json"}

    # If multiple patients with same name, use DOB to distinguish between them
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

    # Determine expected vs actual to adjust scheduling
    actual_minutes = removed_patient.get("actual_duration_minutes") or 0
    expected_minutes = removed_patient.get("expected_duration_minutes")

    # One-way delay to avoid future patients from being scheduled too early
    delta_raw = int(round(actual_minutes - expected_minutes))
    delta_minutes = max(0, delta_raw)

    # Shift room_free_at by the delta so future estimated times account for the delay
    now = datetime.now()
    current_room_free_at = qdoc.get("room_free_at")
    base_time = current_room_free_at if current_room_free_at is not None else now
    new_room_free_at = base_time + timedelta(minutes=delta_minutes)

    # Update the queue: save patients, adjust room_free_at, and accumulate global delay
    queue_collection.update_one(
        {"_id": qdoc["_id"]},
        {
            "$set": {
                "patients": patients,
                "room_free_at": new_room_free_at
            },
            "$inc": {
                "global_delay_minutes": delta_minutes
            }
        }
    )

    return json.dumps({
        "message": "Patient checked out successfully",
        "patient_name": name,
        "status": "completed",
        "actual_duration_minutes": removed_patient.get("actual_duration_minutes"),
        "admitted_at": removed_patient.get("admitted_at").isoformat() if removed_patient.get("admitted_at") else None,
        "completed_at": removed_patient.get("completed_at").isoformat() if removed_patient.get("completed_at") else None,
        "expected_duration_minutes": expected_minutes,
        "delta_minutes": delta_minutes,
        "room_free_at": new_room_free_at.isoformat()
    }), 200, {"Content-Type": "application/json"}

def prune_no_shows():
    if queue_collection is None:
        return
    qdoc = queue_collection.find_one({"queue_id": "main"}) or queue_collection.find_one({})
    if qdoc is None:
        return
    patients = qdoc.get("patients", [])
    if not patients:
        return
    now = datetime.now()
    kept = []
    for p in patients:
        if p.get("checked_in"):
            kept.append(p)
            continue
        deadline = p.get("checkin_deadline")
        if deadline is None or deadline > now:
            kept.append(p)
    if len(kept) != len(patients):
        queue_collection.update_one({"_id": qdoc["_id"]}, {"$set": {"patients": kept}})


def _prune_loop():
    while True:
        try:
            prune_no_shows()
        except Exception:
            pass
        time.sleep(60)


def start_prune_thread():
    t = threading.Thread(target=_prune_loop, daemon=True)
    t.start()

if __name__ == "__main__":
    start_prune_thread()
    app.run(host="127.0.0.1", port=PORT)