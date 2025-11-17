from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

staff_html = """
<!doctype html>
<html>
<head>
    <title>Staff Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
        h2 { color: #343a40; }
        .container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            max-width: 600px;
        }
        .section {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #dee2e6;
        }
        .section:last-child {
            border-bottom: none;
        }
        h3 {
            color: #495057;
            margin-bottom: 15px;
        }
        .search-bar {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 6px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .btn-success {
            background-color: #28a745;
        }
        .btn-success:hover {
            background-color: #218838;
        }
        .result {
            margin-top: 20px;
            background: #e9f7ef;
            padding: 15px;
            border-radius: 8px;
        }
        .result.error {
            background: #f8d7da;
            color: #721c24;
        }
        .result.success {
            background: #d4edda;
            color: #155724;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Urgent Care Staff Dashboard</h2>

        <div class="section">
            <h3>Check In Patient</h3>
            <form method="post" action="/checkin">
                <input type="text" name="patient_name" placeholder="Patient name" required style="width: 100%; margin-bottom: 10px;">
                <input type="date" name="dob" placeholder="DOB (optional for disambiguation)" style="width: 100%; margin-bottom: 10px;">
                <button type="submit" class="btn-success">Check In</button>
            </form>
        </div>

        <div class="section">
            <h3>Admit Patient (Start Appointment)</h3>
            <form method="post" action="/admit">
                <input type="text" name="patient_name" placeholder="Patient name" required style="width: 100%; margin-bottom: 10px;">
                <button type="submit" class="btn-success">Admit</button>
            </form>
        </div>

        <div class="section">
            <h3>Checkout Patient (Complete Appointment)</h3>
            <form method="post" action="/checkout">
                <input type="text" name="patient_name" placeholder="Patient name" required style="width: 100%; margin-bottom: 10px;">
                <button type="submit" class="btn-success">Checkout</button>
            </form>
        </div>

        <div class="section">
            <h3>Search Patient</h3>
            <form method="post" action="/search">
                <div class="search-bar">
                    <input type="text" name="search_name" placeholder="Search patient by name">
                    <button type="submit">Search</button>
                </div>
            </form>
        </div>

        <div class="section">
            <form method="get" action="/show_queue">
                <button type="submit">Show Queue</button>
            </form>
        </div>

        <div class="section">
            <h3 style="color: #dc3545;">⚠️ Reset Queue</h3>
            <p style="color: #6c757d; font-size: 14px;">This will permanently delete all patients from the queue.</p>
            <form method="post" action="/reset_queue" onsubmit="return confirm('Are you sure you want to reset the queue? This cannot be undone.')">
                <button type="submit" style="background-color: #dc3545;">Reset Queue</button>
            </form>
        </div>

        {% if result %}
        <div class="result {{ result_class }}">
            <h3>{{ result_title }}</h3>
            {{ result|safe }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(staff_html)

@app.route("/checkin", methods=["POST"])
def checkin():
    name = request.form.get("patient_name", "").strip()
    dob = request.form.get("dob", "").strip()
    
    if not name:
        return render_template_string(
            staff_html,
            result="Please enter a patient name.",
            result_class="error",
            result_title="Error"
        )
    
    try:
        # Call backend API to check in patient
        data = {"patient_name": name}
        if dob:
            data["dob"] = dob
            
        response = requests.post(
            "http://127.0.0.1:5001/api/patient/checkin",
            data=data
        )
        resp_json = response.json()
        
        if response.status_code == 200:
            scheduled_time = resp_json.get("scheduled_time", "Unknown")
            result_html = f"""
                <p><strong>Patient:</strong> {name}</p>
                <p><strong>Status:</strong> ✓ Checked In</p>
                <p><strong>Scheduled Time:</strong> {scheduled_time}</p>
            """
            return render_template_string(
                staff_html,
                result=result_html,
                result_class="success",
                result_title="Check-In Successful"
            )
        else:
            error_msg = resp_json.get("error", "Patient not found in queue")
            requires_dob = resp_json.get("requires_dob", False)
            if requires_dob:
                error_msg += " Please enter date of birth to disambiguate."
            return render_template_string(
                staff_html,
                result=f"<p>{error_msg}</p>",
                result_class="error",
                result_title="Check-In Failed"
            )
    except Exception as e:
        return render_template_string(
            staff_html,
            result=f"<p>Error connecting to backend: {e}</p>",
            result_class="error",
            result_title="Connection Error"
        )

@app.route("/admit", methods=["POST"])
def admit():
    name = request.form.get("patient_name", "").strip()
    
    if not name:
        return render_template_string(
            staff_html,
            result="Please enter a patient name.",
            result_class="error",
            result_title="Error"
        )
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/api/staff/admit",
            data={"patient_name": name}
        )
        resp_json = response.json()
        
        if response.status_code == 200:
            result_html = f"""
                <p><strong>Patient:</strong> {name}</p>
                <p><strong>Status:</strong> ✓ Admitted (Appointment Started)</p>
            """
            return render_template_string(
                staff_html,
                result=result_html,
                result_class="success",
                result_title="Admit Successful"
            )
        else:
            error_msg = resp_json.get("error", "Failed to admit patient")
            return render_template_string(
                staff_html,
                result=f"<p>{error_msg}</p>",
                result_class="error",
                result_title="Admit Failed"
            )
    except Exception as e:
        return render_template_string(
            staff_html,
            result=f"<p>Error connecting to backend: {e}</p>",
            result_class="error",
            result_title="Connection Error"
        )

@app.route("/checkout", methods=["POST"])
def checkout():
    name = request.form.get("patient_name", "").strip()
    
    if not name:
        return render_template_string(
            staff_html,
            result="Please enter a patient name.",
            result_class="error",
            result_title="Error"
        )
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/api/staff/checkout",
            data={"patient_name": name}
        )
        resp_json = response.json()
        
        if response.status_code == 200:
            duration = resp_json.get("actual_duration_minutes", "N/A")
            admitted_at = resp_json.get("admitted_at", "Unknown")
            completed_at = resp_json.get("completed_at", "Unknown")
            
            result_html = f"""
                <p><strong>Patient:</strong> {name}</p>
                <p><strong>Status:</strong> ✓ Checked Out (Completed)</p>
                <p><strong>Admitted At:</strong> {admitted_at}</p>
                <p><strong>Completed At:</strong> {completed_at}</p>
                <p><strong>Duration:</strong> {duration} minutes</p>
            """
            return render_template_string(
                staff_html,
                result=result_html,
                result_class="success",
                result_title="Checkout Successful"
            )
        else:
            error_msg = resp_json.get("error", "Failed to checkout patient")
            return render_template_string(
                staff_html,
                result=f"<p>{error_msg}</p>",
                result_class="error",
                result_title="Checkout Failed"
            )
    except Exception as e:
        return render_template_string(
            staff_html,
            result=f"<p>Error connecting to backend: {e}</p>",
            result_class="error",
            result_title="Connection Error"
        )

@app.route("/search", methods=["POST"])
def search():
    name = request.form.get("search_name", "").strip()
    # For now, just display what user typed (backend guy will connect this later)
    result_text = f"<p>Searched for patient: {name}</p>" if name else "<p>No name entered.</p>"
    return render_template_string(
        staff_html,
        result=result_text,
        result_class="",
        result_title="Search Result"
    )

@app.route("/show_queue", methods=["GET"])
def show_queue():
    try:
        response = requests.get("http://127.0.0.1:5001/api/staff/queue")
        resp_json = response.json()
        
        if response.status_code == 200:
            patients = resp_json.get("patients", [])
            total = resp_json.get("total_patients", 0)
            global_wait = resp_json.get("global_wait_time_minutes", 0)
            
            if total == 0:
                result_html = "<p>Queue is empty. No patients waiting.</p>"
            else:
                result_html = f"<p><strong>Total Patients:</strong> {total}</p>"
                if global_wait > 0:
                    result_html += f'<p style="color: #dc3545;"><strong>⏱️ Global Wait Time:</strong> +{global_wait} minutes</p>'
                result_html += '<table style="width: 100%; border-collapse: collapse; margin-top: 15px;">'
                result_html += '''<tr style="background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 8px; text-align: left;">#</th>
                    <th style="padding: 8px; text-align: left;">Name</th>
                    <th style="padding: 8px; text-align: left;">Status</th>
                    <th style="padding: 8px; text-align: left;">Scheduled Time</th>
                    <th style="padding: 8px; text-align: left;">Symptoms</th>
                </tr>'''
                
                for patient in patients:
                    pos = patient.get("position", 0) + 1
                    name = patient.get("name", "Unknown")
                    status = patient.get("status", "waiting")
                    scheduled = patient.get("scheduled_time", "N/A")
                    symptoms = patient.get("symptoms", "N/A")
                    
                    # Color code status
                    status_color = {
                        "waiting": "#6c757d",
                        "checked_in": "#007bff",
                        "admitted": "#28a745",
                        "completed": "#17a2b8"
                    }.get(status, "#6c757d")
                    
                    status_icon = {
                        "waiting": "⏳",
                        "checked_in": "✓",
                        "admitted": "🏥",
                        "completed": "✅"
                    }.get(status, "")
                    
                    result_html += f'''<tr style="border-bottom: 1px solid #dee2e6;">
                        <td style="padding: 8px;">{pos}</td>
                        <td style="padding: 8px;"><strong>{name}</strong></td>
                        <td style="padding: 8px; color: {status_color};">{status_icon} {status}</td>
                        <td style="padding: 8px; font-size: 12px;">{scheduled}</td>
                        <td style="padding: 8px; font-size: 12px;">{symptoms[:50]}...</td>
                    </tr>'''
                
                result_html += '</table>'
            
            return render_template_string(
                staff_html,
                result=result_html,
                result_class="",
                result_title="Current Queue"
            )
        else:
            error_msg = resp_json.get("error", "Failed to get queue")
            return render_template_string(
                staff_html,
                result=f"<p>{error_msg}</p>",
                result_class="error",
                result_title="Queue Error"
            )
    except Exception as e:
        return render_template_string(
            staff_html,
            result=f"<p>Error connecting to backend: {e}</p>",
            result_class="error",
            result_title="Connection Error"
        )

@app.route("/reset_queue", methods=["POST"])
def reset_queue():
    try:
        response = requests.post("http://127.0.0.1:5001/api/staff/reset")
        resp_json = response.json()
        
        if response.status_code == 200:
            result_html = """
                <p><strong>✓ Queue has been reset successfully</strong></p>
                <p>All patients have been removed and queue has been reinitialized.</p>
            """
            return render_template_string(
                staff_html,
                result=result_html,
                result_class="success",
                result_title="Queue Reset"
            )
        else:
            error_msg = resp_json.get("error", "Failed to reset queue")
            return render_template_string(
                staff_html,
                result=f"<p>{error_msg}</p>",
                result_class="error",
                result_title="Reset Failed"
            )
    except Exception as e:
        return render_template_string(
            staff_html,
            result=f"<p>Error connecting to backend: {e}</p>",
            result_class="error",
            result_title="Connection Error"
        )

if __name__ == "__main__":
    app.run(debug=True, port=5002)
