from datetime import datetime, timedelta
import unittest
from q_system import PatientQueue
from patient import Patient

class TestPatientQueue(unittest.TestCase):

    def setUp(self):
        start_time = datetime(2025, 9, 18, 9, 0)
        self.pq = PatientQueue(slot_seconds=900, start_time=start_time)  # 15-minute slots

    def test_enqueue_patients(self):
        p1 = Patient()
        p1.personal.first_name = "John"
        p1.personal.last_name = "Doe"
        p1.visit.chief_complaint = "Cough and fever"

        p2 = Patient()
        p2.personal.first_name = "Jane"
        p2.personal.last_name = "Smith"
        p2.visit.chief_complaint = "Sprained ankle"

        time1 = self.pq.enqueue(p1)
        time2 = self.pq.enqueue(p2)

        self.assertEqual(time1, datetime(2025, 9, 18, 9, 0))
        self.assertEqual(time2, datetime(2025, 9, 18, 9, 15))

    def test_peek_next_patient(self):
        p1 = Patient()
        p1.personal.first_name = "John"
        p1.personal.last_name = "Doe"
        p1.visit.chief_complaint = "Cough and fever"
        self.pq.enqueue(p1)

        next_patient = self.pq.peek()
        self.assertIsNotNone(next_patient)
        self.assertEqual(next_patient.full_name(), "John Doe")

    def test_schedule_times(self):
        p1 = Patient()
        p1.personal.first_name = "John"
        p1.personal.last_name = "Doe"
        p1.visit.chief_complaint = "Cough and fever"

        p2 = Patient()
        p2.personal.first_name = "Jane"
        p2.personal.last_name = "Smith"
        p2.visit.chief_complaint = "Sprained ankle"

        self.pq.enqueue(p1)
        self.pq.enqueue(p2)

        scheduled_times = [patient.visit.scheduled_time for patient in self.pq.patients]
        expected_times = [
            datetime(2025, 9, 18, 9, 0),
            datetime(2025, 9, 18, 9, 15)
        ]

        self.assertEqual(scheduled_times, expected_times)

if __name__ == '__main__':
    unittest.main()