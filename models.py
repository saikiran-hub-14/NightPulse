from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))

    
class Patient(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    # Basic Details
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))

    # Medical Details
    blood_group = db.Column(db.String(10))
    disease = db.Column(db.String(200))
    allergies = db.Column(db.String(200))

    # Admission Details
    admission_date = db.Column(db.String(50))
    ward = db.Column(db.String(50))
    room = db.Column(db.String(50))

    # Monitoring Setup
    severity = db.Column(db.String(20))
    doctor_id = db.Column(db.Integer)
    device_id = db.Column(db.Integer)

    # Billing
    payment_status = db.Column(db.String(20))
class Device(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    device_code = db.Column(db.String(50))
    battery = db.Column(db.Integer)
    status = db.Column(db.String(50))
    assigned_patient = db.Column(db.Integer)


class HealthData(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    bp = db.Column(db.String(20))
    temperature = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)


class Alert(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer)
    alert_type = db.Column(db.String(50))
    alert_level = db.Column(db.String(50))
    doctor_response = db.Column(db.String(50), default="Pending")
    escalation_status = db.Column(db.String(50), default="No")
    timestamp = db.Column(db.DateTime)