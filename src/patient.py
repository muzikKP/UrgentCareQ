class Address:
  def __init__(self):
    # self.street = ""
    # self.city = ""
    # self.state = ""
    self.zip = ""

class EmergencyContact:
  def __init__(self):
    self.name = ""
    self.relationship = ""
    self.phone = ""

class PersonalContact:
  def __init__(self):
    self.first_name = ""
    self.middle_initial = ""
    self.last_name = ""
    self.dob = ""
    self.sex_or_gender = ""
    self.phone_primary = ""
    self.phone_secondary = ""
    self.email = ""
    self.address = Address()
    self.emergency_contact = EmergencyContact()

class InsuranceInfo:
  def __init__(self):
    # self.government_id_type = ""
    # self.government_id_number = ""
    self.provider = ""
    self.plan = ""
    self.policy_number = ""
    self.group_number = ""
    # self.subscriber_name = ""
    # self.subscriber_relation = ""
    # self.copay_method = ""

class VisitReason:
  def __init__(self):
    self.chief_complaint = ""
    self.symptom_onset = ""
    self.severity = ""
    self.relevant_history = []
    self.injury_details = ""

class MedicalHistory:
  def __init__(self):
    self.allergies = []
    self.current_medications = []
    self.past_conditions = []
    self.past_surgeries_or_hospitalizations = []
    self.immunization_status = ""
    self.pregnancy_status = None
    self.primary_care_provider = ""

class Administrative:
  def __init__(self):
    self.consent_to_treatment = False
    self.hipaa_acknowledgment = False
    self.financial_responsibility_ack = False
    self.photo_release_ack = False
    self.notes = ""
    self.checked_in = False

class Patient:
  def __init__(self):
    self.personal = PersonalContact()
    self.insurance = InsuranceInfo()
    self.visit = VisitReason()
    self.history = MedicalHistory()
    self.admin = Administrative()

  def full_name(self):
    mi = f" {self.personal.middle_initial}." if self.personal.middle_initial else ""
    return f"{self.personal.first_name}{mi} {self.personal.last_name}".strip()