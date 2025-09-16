from datetime import datetime, timedelta

class PatientQueue:
  def __init__(self, slot_seconds=600, start_time=None):
    self.slot_seconds = slot_seconds
    self.start_time = start_time
    self.q = []
    self.last_assigned = None

  def _now(self):
    return datetime.now()

  def _next_time(self):
    if self.last_assigned is None:
      return self.start_time if self.start_time is not None else self._now()
    return self.last_assigned + timedelta(seconds=self.slot_seconds)

  def enqueue(self, p):
    t = self._next_time()
    p.visit.scheduled_time = t.strftime("%Y-%m-%d %H:%M")
    self.last_assigned = t
    self.q.append(p)
    return p.visit.scheduled_time

  def dequeue(self):
    if not self.q:
      return None
    return self.q.pop(0)

  def peek(self):
    return self.q[0] if self.q else None

  def size(self):
    return len(self.q)

  def schedule_snapshot(self):
    return [(p.full_name(), getattr(p.visit, "scheduled_time", None)) for p in self.q]
