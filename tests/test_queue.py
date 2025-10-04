from datetime import datetime, timedelta
import unittest
import sys
import os

# Add src directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from q_system import PatientQueue
from patient import Patient


class TestPatientQueue(unittest.TestCase):
    """Comprehensive tests for PatientQueue functionality."""

    def setUp(self):
        """Set up test fixtures with a deterministic start time."""
        self.start_time = datetime(2025, 10, 4, 9, 0)  # 9:00 AM on Oct 4, 2025
        self.pq = PatientQueue(slot_seconds=900, start_time=self.start_time)  # 15-minute slots

    def _create_patient(self, first_name, last_name, complaint="General checkup"):
        """Helper method to create a patient."""
        patient = Patient()
        patient.personal.first_name = first_name
        patient.personal.last_name = last_name
        patient.visit.chief_complaint = complaint
        return patient

    # ===== Basic Enqueue/Dequeue Tests =====

    def test_enqueue_single_patient(self):
        """Test enqueueing a single patient."""
        p1 = self._create_patient("John", "Doe", "Cough and fever")
        scheduled_time = self.pq.enqueue(p1)
        
        self.assertEqual(self.pq.size(), 1)
        self.assertEqual(p1.visit.scheduled_time, self.start_time)
        self.assertEqual(scheduled_time, self.start_time)

    def test_enqueue_multiple_patients(self):
        """Test enqueueing multiple patients with correct time slots."""
        p1 = self._create_patient("John", "Doe", "Cough and fever")
        p2 = self._create_patient("Jane", "Smith", "Sprained ankle")
        p3 = self._create_patient("Bob", "Johnson", "Headache")

        time1 = self.pq.enqueue(p1)
        time2 = self.pq.enqueue(p2)
        time3 = self.pq.enqueue(p3)

        # Check queue size
        self.assertEqual(self.pq.size(), 3)
        
        # Check scheduled times (datetime objects)
        self.assertEqual(p1.visit.scheduled_time, self.start_time)
        self.assertEqual(p2.visit.scheduled_time, self.start_time + timedelta(seconds=900))
        self.assertEqual(p3.visit.scheduled_time, self.start_time + timedelta(seconds=1800))
        
        # Check returned datetime objects
        self.assertEqual(time1, self.start_time)
        self.assertEqual(time2, self.start_time + timedelta(seconds=900))
        self.assertEqual(time3, self.start_time + timedelta(seconds=1800))

    def test_dequeue_patient(self):
        """Test dequeueing patients in FIFO order."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        
        # Dequeue first patient
        dequeued = self.pq.dequeue()
        self.assertEqual(dequeued.full_name(), "John Doe")
        self.assertEqual(self.pq.size(), 1)
        
        # Dequeue second patient
        dequeued = self.pq.dequeue()
        self.assertEqual(dequeued.full_name(), "Jane Smith")
        self.assertEqual(self.pq.size(), 0)

    def test_dequeue_empty_queue(self):
        """Test dequeueing from an empty queue returns None."""
        result = self.pq.dequeue()
        self.assertIsNone(result)

    def test_peek_patient(self):
        """Test peeking at next patient without removing them."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        
        # Peek should return first patient without removing
        peeked = self.pq.peek()
        self.assertEqual(peeked.full_name(), "John Doe")
        self.assertEqual(self.pq.size(), 2)  # Size unchanged
        
        # Peek again should return same patient
        peeked_again = self.pq.peek()
        self.assertEqual(peeked_again.full_name(), "John Doe")

    def test_peek_empty_queue(self):
        """Test peeking at an empty queue returns None."""
        result = self.pq.peek()
        self.assertIsNone(result)

    # ===== Patient Removal Tests =====

    def test_remove_patient_by_object(self):
        """Test removing a specific patient by object reference."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        p3 = self._create_patient("Bob", "Johnson")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        self.pq.enqueue(p3)
        
        # Remove middle patient
        result = self.pq.remove_patient(p2)
        self.assertTrue(result)
        self.assertEqual(self.pq.size(), 2)
        
        # Verify remaining patients
        patients = self.pq.get_all_patients()
        self.assertEqual(len(patients), 2)
        self.assertEqual(patients[0].full_name(), "John Doe")
        self.assertEqual(patients[1].full_name(), "Bob Johnson")

    def test_remove_patient_not_in_queue(self):
        """Test removing a patient that's not in the queue returns False."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        
        self.pq.enqueue(p1)
        
        result = self.pq.remove_patient(p2)
        self.assertFalse(result)
        self.assertEqual(self.pq.size(), 1)

    def test_remove_patient_by_name(self):
        """Test removing a patient by full name."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        p3 = self._create_patient("Bob", "Johnson")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        self.pq.enqueue(p3)
        
        # Remove by name
        result = self.pq.remove_patient_by_name("Jane Smith")
        self.assertTrue(result)
        self.assertEqual(self.pq.size(), 2)
        
        # Verify patient was removed
        names = [p.full_name() for p in self.pq.get_all_patients()]
        self.assertNotIn("Jane Smith", names)
        self.assertIn("John Doe", names)
        self.assertIn("Bob Johnson", names)

    def test_remove_patient_by_name_not_found(self):
        """Test removing a patient by name that doesn't exist."""
        p1 = self._create_patient("John", "Doe")
        self.pq.enqueue(p1)
        
        result = self.pq.remove_patient_by_name("Jane Smith")
        self.assertFalse(result)
        self.assertEqual(self.pq.size(), 1)

    def test_remove_patient_by_name_with_middle_initial(self):
        """Test removing a patient with a middle initial."""
        p1 = self._create_patient("John", "Doe")
        p1.personal.middle_initial = "Q"
        self.pq.enqueue(p1)
        
        # Should match full name with middle initial
        result = self.pq.remove_patient_by_name("John Q. Doe")
        self.assertTrue(result)
        self.assertEqual(self.pq.size(), 0)

    def test_remove_at_index(self):
        """Test removing a patient at a specific index."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        p3 = self._create_patient("Bob", "Johnson")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        self.pq.enqueue(p3)
        
        # Remove at index 1 (Jane Smith)
        removed = self.pq.remove_at_index(1)
        self.assertIsNotNone(removed)
        self.assertEqual(removed.full_name(), "Jane Smith")
        self.assertEqual(self.pq.size(), 2)
        
        # Verify remaining patients
        names = [p.full_name() for p in self.pq.get_all_patients()]
        self.assertEqual(names, ["John Doe", "Bob Johnson"])

    def test_remove_at_index_first(self):
        """Test removing the first patient (index 0)."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        
        removed = self.pq.remove_at_index(0)
        self.assertEqual(removed.full_name(), "John Doe")
        self.assertEqual(self.pq.peek().full_name(), "Jane Smith")

    def test_remove_at_index_last(self):
        """Test removing the last patient."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        
        removed = self.pq.remove_at_index(1)
        self.assertEqual(removed.full_name(), "Jane Smith")
        self.assertEqual(self.pq.size(), 1)

    def test_remove_at_invalid_index(self):
        """Test removing at invalid indices returns None."""
        p1 = self._create_patient("John", "Doe")
        self.pq.enqueue(p1)
        
        # Negative index
        result = self.pq.remove_at_index(-1)
        self.assertIsNone(result)
        
        # Index too large
        result = self.pq.remove_at_index(10)
        self.assertIsNone(result)
        
        # Queue size unchanged
        self.assertEqual(self.pq.size(), 1)

    def test_clear_schedule(self):
        """Test clearing all patients from the schedule."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        p3 = self._create_patient("Bob", "Johnson")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        self.pq.enqueue(p3)
        
        self.pq.clear_schedule()
        
        self.assertEqual(self.pq.size(), 0)
        self.assertIsNone(self.pq.peek())
        self.assertEqual(len(self.pq.get_all_patients()), 0)

    # ===== Schedule Information Tests =====

    def test_get_all_patients(self):
        """Test getting all patients returns correct list."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        
        all_patients = self.pq.get_all_patients()
        self.assertEqual(len(all_patients), 2)
        self.assertEqual(all_patients[0].full_name(), "John Doe")
        self.assertEqual(all_patients[1].full_name(), "Jane Smith")

    def test_get_all_patients_returns_copy(self):
        """Test that get_all_patients returns a copy, not the original list."""
        p1 = self._create_patient("John", "Doe")
        self.pq.enqueue(p1)
        
        patients_list = self.pq.get_all_patients()
        patients_list.clear()  # Clear the returned list
        
        # Original queue should be unchanged
        self.assertEqual(self.pq.size(), 1)

    def test_get_scheduled_times(self):
        """Test getting scheduled times for all patients."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        
        scheduled_times = self.pq.get_scheduled_times()
        
        self.assertEqual(len(scheduled_times), 2)
        self.assertEqual(scheduled_times[0][0], "John Doe")
        self.assertEqual(scheduled_times[0][1], self.start_time)
        self.assertEqual(scheduled_times[1][0], "Jane Smith")
        self.assertEqual(scheduled_times[1][1], self.start_time + timedelta(seconds=900))

    # ===== Edge Cases and Special Scenarios =====

    def test_empty_queue_operations(self):
        """Test various operations on an empty queue."""
        self.assertEqual(self.pq.size(), 0)
        self.assertIsNone(self.pq.peek())
        self.assertIsNone(self.pq.dequeue())
        self.assertEqual(len(self.pq.get_all_patients()), 0)
        self.assertEqual(len(self.pq.get_scheduled_times()), 0)

    def test_different_slot_sizes(self):
        """Test queue with different slot durations."""
        # 30-minute slots
        pq_30min = PatientQueue(slot_seconds=1800, start_time=self.start_time)
        
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        
        pq_30min.enqueue(p1)
        pq_30min.enqueue(p2)
        
        self.assertEqual(p1.visit.scheduled_time, self.start_time)
        self.assertEqual(p2.visit.scheduled_time, self.start_time + timedelta(seconds=1800))

    def test_patient_full_name_formatting(self):
        """Test that patient full names are correctly formatted."""
        p1 = self._create_patient("John", "Doe")
        p1.personal.middle_initial = "Q"
        self.pq.enqueue(p1)
        
        self.assertEqual(p1.full_name(), "John Q. Doe")
        
        # Without middle initial
        p2 = self._create_patient("Jane", "Smith")
        self.pq.enqueue(p2)
        self.assertEqual(p2.full_name(), "Jane Smith")

    def test_enqueue_after_removal(self):
        """Test that enqueueing after removal continues from last assigned time."""
        p1 = self._create_patient("John", "Doe")
        p2 = self._create_patient("Jane", "Smith")
        p3 = self._create_patient("Bob", "Johnson")
        
        self.pq.enqueue(p1)  # 9:00
        self.pq.enqueue(p2)  # 9:15
        
        # Remove first patient
        self.pq.remove_at_index(0)
        
        # Next enqueue should still be at 9:30 (continues from last assigned)
        self.pq.enqueue(p3)
        self.assertEqual(p3.visit.scheduled_time, self.start_time + timedelta(seconds=1800))

    def test_multiple_patients_same_name(self):
        """Test handling multiple patients with the same name."""
        p1 = self._create_patient("John", "Doe", "Fever")
        p2 = self._create_patient("John", "Doe", "Cough")
        
        self.pq.enqueue(p1)
        self.pq.enqueue(p2)
        
        # Remove by name should only remove the first one
        result = self.pq.remove_patient_by_name("John Doe")
        self.assertTrue(result)
        self.assertEqual(self.pq.size(), 1)
        
        # Remaining patient should have "Cough" complaint
        remaining = self.pq.peek()
        self.assertEqual(remaining.visit.chief_complaint, "Cough")


class TestPatientModel(unittest.TestCase):
    """Test the Patient data model."""

    def test_patient_initialization(self):
        """Test that a new patient has all required attributes."""
        patient = Patient()
        
        self.assertIsNotNone(patient.personal)
        self.assertIsNotNone(patient.insurance)
        self.assertIsNotNone(patient.visit)
        self.assertIsNotNone(patient.history)
        self.assertIsNotNone(patient.admin)

    def test_full_name_basic(self):
        """Test basic full name generation."""
        patient = Patient()
        patient.personal.first_name = "John"
        patient.personal.last_name = "Doe"
        
        self.assertEqual(patient.full_name(), "John Doe")

    def test_full_name_with_middle_initial(self):
        """Test full name with middle initial."""
        patient = Patient()
        patient.personal.first_name = "John"
        patient.personal.middle_initial = "Q"
        patient.personal.last_name = "Doe"
        
        self.assertEqual(patient.full_name(), "John Q. Doe")

    def test_full_name_empty(self):
        """Test full name with empty strings."""
        patient = Patient()
        self.assertEqual(patient.full_name(), "")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)