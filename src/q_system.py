from datetime import timedelta

class PatientQueue:
    def __init__(self, slot_seconds=900, start_time=None):
        self.slot_seconds  = slot_seconds
        self.start_time = start_time
        self.queue = []
        self.current_time = start_time

    def enqueue(self, patient):
        scheduled_time = self.get_next_available_time()
        patient.visit.scheduled_time = scheduled_time
        self.queue.append(patient)
        return scheduled_time

    def get_next_available_time(self):
        if not self.queue:
            return self.start_time
        else:
            last_patient_time = self.queue[-1].visit.scheduled_time
            return last_patient_time + timedelta(seconds=self.slot_seconds)

    def peek(self):
        return self.queue[0] if self.queue else None

    def size(self):
        return len(self.queue)

    def dequeue(self):
        return self.queue.pop(0) if self.queue else None

    def advance_time(self):
        if self.current_time:
            self.current_time += timedelta(seconds=self.slot_seconds)

    def get_scheduled_times(self):
        return [(patient.full_name(), patient.visit.scheduled_time) for patient in self.queue]

    # added: return list of patients (used by main.py)
    def get_all_patients(self):
        return list(self.queue)