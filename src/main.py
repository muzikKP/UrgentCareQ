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

    # Enqueue patients and print their scheduled times
    scheduled_time_p1 = pq.enqueue(p1)
    print(f"Scheduling {p1.full_name()} at {scheduled_time_p1}")

    scheduled_time_p2 = pq.enqueue(p2)
    print(f"Scheduling {p2.full_name()} at {scheduled_time_p2}")

    # Peek at the next patient
    next_patient = pq.peek()
    if next_patient:
        print(f"Next patient: {next_patient.full_name()} scheduled at {next_patient.visit.scheduled_time}")

    # Instead of dequeuing, just print the scheduled times
    print("Scheduled patients:")
    for patient in pq.get_all_patients():
        print(f"{patient.full_name()} is scheduled at {patient.visit.scheduled_time}")


if __name__ == "__main__":
    main()