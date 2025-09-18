from datetime import datetime, timedelta

class Scheduler:
    def __init__(self, slot_seconds=900, start_time=None):
        self.slot_seconds = slot_seconds
        self.start_time = start_time if start_time else datetime.now()
        self.schedule = []

    def schedule_patient(self, patient):
        scheduled_time = self.start_time + timedelta(seconds=len(self.schedule) * self.slot_seconds)
        self.schedule.append((patient, scheduled_time))
        return scheduled_time

    def get_schedule(self):
        return [(patient.full_name(), scheduled_time) for patient, scheduled_time in self.schedule]

    def next_patient_time(self):
        if self.schedule:
            return self.schedule[0][1]
        return None

    def size(self):
        return len(self.schedule)