from q_system import PatientQueue
from patient import Patient

def main():
  pq = PatientQueue(slot_seconds=900)  # 15-minute slots

  p1 = Patient()
  p1.personal.first_name = "John"
  p1.personal.last_name = "Doe"
  p1.visit.chief_complaint = "Cough and fever"

  p2 = Patient()
  p2.personal.first_name = "Jane"
  p2.personal.last_name = "Smith"
  p2.visit.chief_complaint = "Sprained ankle"

  # Enqueue patients
  print(f"Scheduling {p1.full_name()} at {pq.enqueue(p1)}")
  print(f"Scheduling {p2.full_name()} at {pq.enqueue(p2)}")

  # Peek at the next patient
  next_patient = pq.peek()
  if next_patient:
    print(f"Next patient: {next_patient.full_name()} scheduled at {next_patient.visit.scheduled_time}")

  # Dequeue patients as they are seen
  while pq.size() > 0:
    seen_patient = pq.dequeue()
    print(f"Seeing patient: {seen_patient.full_name()} who was scheduled at {seen_patient.visit.scheduled_time}")


if __name__ == "__main__":
  main()