from datetime import timedelta

class PatientQueue:
    def __init__(self, slot_seconds=900, start_time=None):
        self.slot_seconds = slot_seconds
        self.start_time = start_time
        self.patients = []  # renamed from queue to patients for clarity
        self.current_time = start_time

    def enqueue(self, patient):
        scheduled_time = self.get_next_available_time()
        patient.visit.scheduled_time = scheduled_time
        self.patients.append(patient)
        return scheduled_time

    def get_next_available_time(self):
        if not self.patients:
            return self.start_time
        else:
            last_patient_time = self.patients[-1].visit.scheduled_time
            return last_patient_time + timedelta(seconds=self.slot_seconds)

    def peek(self):
        return self.patients[0] if self.patients else None

    def size(self):
        return len(self.patients)

    def dequeue(self):
        return self.patients.pop(0) if self.patients else None

    def advance_time(self):
        if self.current_time:
            self.current_time += timedelta(seconds=self.slot_seconds)

    def get_scheduled_times(self):
        return [(patient.full_name(), patient.visit.scheduled_time) for patient in self.patients]

    def get_all_patients(self):
        return list(self.patients)

    # New: Find and return a patient by name
    def find_patient_by_name(self, full_name):
        """Find and return the first patient matching the full name. Returns None if not found."""
        for patient in self.patients:
            if patient.full_name() == full_name:
                return patient
        return None

    # New: Remove a specific patient by object reference
    def remove_patient(self, patient):
        """Remove a specific patient from the schedule. Returns True if removed, False if not found."""
        if patient in self.patients:
            self.patients.remove(patient)
            return True
        return False

    # New: Remove patient by full name
    def remove_patient_by_name(self, full_name):
        """Remove the first patient matching the full name. Returns True if removed, False if not found."""
        for patient in self.patients:
            if patient.full_name() == full_name:
                self.patients.remove(patient)
                return True
        return False

    # New: Remove patient at a specific index
    def remove_at_index(self, index):
        """Remove patient at the given index. Returns the removed patient or None if index is invalid."""
        if 0 <= index < len(self.patients):
            return self.patients.pop(index)
        return None

    # New: Clear all patients from schedule
    def clear_schedule(self):
        """Remove all patients from the schedule."""
        self.patients.clear()