from flask import Flask, render_template, request, redirect, session
from models import db, Patient, Alert, Device, User
from datetime import datetime
import threading
import time
import random

app = Flask(__name__)
app.secret_key = "nightpulse_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nightpulse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ---------------- LOGIN ---------------- #

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        user_id = request.form["user_id"]
        password = request.form["password"]
        role = request.form["role"]

        user = User.query.filter_by(
            user_id=user_id,
            password=password,
            role=role
        ).first()

        if user:

            session["user"] = user_id
            session["role"] = role

            if role == "admin":
                return redirect("/admin")

            if role == "doctor":
                return redirect("/doctor_dashboard")

        return "Invalid Login"

    return render_template("login.html")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- ADMIN DASHBOARD ---------------- #

@app.route("/admin")
def admin_dashboard():

    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    total_patients = Patient.query.count()
    critical_patients = Patient.query.filter_by(severity="Critical").count()
    moderate_patients = Patient.query.filter_by(severity="Moderate").count()
    total_devices = Device.query.count()
    active_alerts = Alert.query.filter_by(doctor_response="Pending").count()

    return render_template(
        "admin_dashboard.html",
        total_patients=total_patients,
        critical_patients=critical_patients,
        moderate_patients=moderate_patients,
        total_devices=total_devices,
        active_alerts=active_alerts
    )


# ---------------- ADD PATIENT ---------------- #

@app.route("/add_patient", methods=["GET","POST"])
def add_patient():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        patient = Patient(
            name=request.form["name"],
            age=request.form["age"],
            gender=request.form["gender"],
            phone=request.form["phone"],
            address=request.form["address"],
            blood_group=request.form["blood_group"],
            disease=request.form["disease"],
            allergies=request.form["allergies"],
            admission_date=request.form["admission_date"],
            ward=request.form["ward"],
            room=request.form["room"],
            severity=request.form["severity"],
            doctor_id=request.form["doctor_id"],
            device_id=request.form["device_id"],
            payment_status=request.form["payment_status"]
        )

        db.session.add(patient)
        db.session.commit()

        return redirect("/admin")

    return render_template("add_patient.html")


# ---------------- PATIENT LIST ---------------- #

@app.route("/patients")
def patients():

    if "user" not in session:
        return redirect("/")

    all_patients = Patient.query.all()

    return render_template("patients.html", patients=all_patients)


@app.route("/discharge_patient/<int:patient_id>")
def discharge_patient(patient_id):

    if "user" not in session:
        return redirect("/")

    patient = Patient.query.get(patient_id)

    if patient:
        db.session.delete(patient)
        db.session.commit()

    return redirect("/patients")


# ---------------- DOCTOR DASHBOARD ---------------- #

@app.route("/doctor_dashboard")
def doctor_dashboard():

    if "user" not in session or session["role"] != "doctor":
        return redirect("/")

    doctor_id = 1

    patients = Patient.query.filter_by(doctor_id=doctor_id).all()

    return render_template(
        "doctor_dashboard.html",
        patients=patients
    )


# ---------------- PATIENT MONITOR ---------------- #

@app.route("/monitor/<int:patient_id>")
def monitor(patient_id):

    if "user" not in session:
        return redirect("/")

    patient = Patient.query.get(patient_id)

    return render_template("patient_monitor.html", patient=patient)


# ---------------- ALERT ESCALATION ---------------- #

def escalate(alert_id):

    time.sleep(60)

    with app.app_context():

        alert = Alert.query.get(alert_id)

        if alert and alert.doctor_response == "Pending":

            alert.escalation_status = "Yes"
            db.session.commit()


# ---------------- CREATE ALERT ---------------- #

@app.route("/create_alert/<int:patient_id>/<alert_type>")
def create_alert(patient_id, alert_type):

    new_alert = Alert(
        patient_id=patient_id,
        alert_type=alert_type,
        alert_level="Critical",
        doctor_response="Pending",
        escalation_status="No",
        timestamp=datetime.now()
    )

    db.session.add(new_alert)
    db.session.commit()

    threading.Thread(target=escalate, args=(new_alert.id,)).start()

    return "Alert Created"


# ---------------- ALERT PAGE ---------------- #

@app.route("/alerts")
def alerts():

    if "user" not in session:
        return redirect("/")

    alerts = Alert.query.all()

    return render_template("alerts.html", alerts=alerts)


@app.route("/doctor_alerts")
def doctor_alerts():

    if "user" not in session or session["role"] != "doctor":
        return redirect("/")

    alerts = Alert.query.order_by(Alert.id.desc()).all()

    return render_template("doctor_alerts.html", alerts=alerts)


# ---------------- ACKNOWLEDGE ALERT ---------------- #

@app.route("/resolve_alert/<int:alert_id>")
def resolve_alert(alert_id):

    if "user" not in session:
        return redirect("/")

    alert = Alert.query.get(alert_id)

    if alert:
        alert.doctor_response = "Responded"
        db.session.commit()

    if session["role"] == "doctor":
        return redirect("/doctor_alerts")

    return redirect("/alerts")


# ---------------- DEVICE MANAGEMENT ---------------- #

@app.route("/devices")
def devices():

    if "user" not in session:
        return redirect("/")

    devices = Device.query.all()

    return render_template("devices.html", devices=devices)


@app.route("/add_device", methods=["GET","POST"])
def add_device():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        battery = random.randint(20,100)

        device = Device(
            device_code=request.form["device_code"],
            battery=battery,
            status=request.form["status"],
            assigned_patient=request.form["assigned_patient"]
        )

        db.session.add(device)
        db.session.commit()

        return redirect("/devices")

    return render_template("add_device.html")


@app.route("/edit_device/<int:device_id>", methods=["GET","POST"])
def edit_device(device_id):

    if "user" not in session:
        return redirect("/")

    device = Device.query.get(device_id)

    if request.method == "POST":

        device.status = request.form["status"]
        device.assigned_patient = request.form["assigned_patient"]

        db.session.commit()

        return redirect("/devices")

    return render_template("edit_device.html", device=device)


@app.route("/delete_device/<int:device_id>")
def delete_device(device_id):

    if "user" not in session:
        return redirect("/")

    device = Device.query.get(device_id)

    if device:
        db.session.delete(device)
        db.session.commit()

    return redirect("/devices")


# ---------------- ALERT API ---------------- #

@app.route("/get_alerts")
def get_alerts():

    alerts = Alert.query.order_by(Alert.id.desc()).limit(5).all()

    alert_list = []

    for a in alerts:

        alert_list.append({
            "patient": a.patient_id,
            "type": a.alert_type,
            "level": a.alert_level
        })

    return {"alerts": alert_list}


# ---------------- ALERT SIMULATION ---------------- #

def simulate_alerts():

    while True:

        time.sleep(20)

        with app.app_context():

            patients = Patient.query.all()

            if not patients:
                continue

            patient = random.choice(patients)

            alert_types = [
                "Heart Rate High",
                "Low Oxygen",
                "High Temperature"
            ]

            new_alert = Alert(
                patient_id=patient.id,
                alert_type=random.choice(alert_types),
                alert_level="Critical",
                doctor_response="Pending",
                escalation_status="No",
                timestamp=datetime.now()
            )

            db.session.add(new_alert)
            db.session.commit()


# ---------------- CREATE DEFAULT USERS ---------------- #

@app.route("/create_users")
def create_users():

    admin = User(user_id="admin", password="admin123", role="admin")
    doctor = User(user_id="doctor1", password="doctor123", role="doctor")

    db.session.add(admin)
    db.session.add(doctor)
    db.session.commit()

    return "Users Created"


# ---------------- RUN SERVER ---------------- #

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    threading.Thread(target=simulate_alerts, daemon=True).start()

    app.run(debug=True)