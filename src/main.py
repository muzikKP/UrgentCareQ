from q_system import PatientQueue
from patient import Patient
from datetime import datetime, timedelta


def main():
    # Use the current time for real-time scheduling
    start = datetime.now()
    pq = PatientQueue(slot_seconds=900, start_time=start)  # 15-minute slots

    p1 = Patient()
    p1.personal.first_name = "John"
    p1.personal.last_name = "Doe"
    p1.visit.chief_complaint = "Cough and fever"

    p2 = Patient()
    p2.personal.first_name = "Jane"
    p2.personal.last_name = "Smith"
    p2.visit.chief_complaint = "Sprained ankle"

    p3 = Patient()
    p3.personal.first_name = "Bob"
    p3.personal.last_name = "Johnson"
    p3.visit.chief_complaint = "Headache"

    # Enqueue patients and print their scheduled times
    scheduled_time_p1 = pq.enqueue(p1)
    print(f"Scheduling {p1.full_name()} at {scheduled_time_p1}")

    scheduled_time_p2 = pq.enqueue(p2)
    print(f"Scheduling {p2.full_name()} at {scheduled_time_p2}")

    scheduled_time_p3 = pq.enqueue(p3)
    print(f"Scheduling {p3.full_name()} at {scheduled_time_p3}")

    print("\n--- Initial Schedule ---")
    for patient in pq.get_all_patients():
        print(f"{patient.full_name()} is scheduled at {patient.visit.scheduled_time}")

    # Demo: Remove Jane Smith by name
    print("\n--- Removing Jane Smith ---")
    removed = pq.remove_patient_by_name("Jane Smith")
    print(f"Removed: {removed}")

    print("\n--- Updated Schedule ---")
    for patient in pq.get_all_patients():
        print(f"{patient.full_name()} is scheduled at {patient.visit.scheduled_time}")

    # Demo: Remove patient at index 0 (John Doe)
    print("\n--- Removing patient at index 0 ---")
    removed_patient = pq.remove_at_index(0)
    if removed_patient:
        print(f"Removed {removed_patient.full_name()}")

    print("\n--- Final Schedule ---")
    for patient in pq.get_all_patients():
        print(f"{patient.full_name()} is scheduled at {patient.visit.scheduled_time}")


if __name__ == "__main__":
    main()