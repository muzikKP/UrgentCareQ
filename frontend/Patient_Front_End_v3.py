from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

form_html = """
<!doctype html>
<html>
<head>
    <title>Patient Check-In</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
        h2 { color: #007bff; }
        form, .result {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            max-width: 400px;
        }
        input, textarea {
            width: 100%;
            padding: 8px;
            margin-top: 4px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        input[type="submit"] {
            background-color: #007bff;
            color: white;
            cursor: pointer;
            border: none;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
        .info {
            margin-top: 20px;
            background: #e9f7ef;
            padding: 15px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <h2>Urgent Care Patient Registration</h2>
    <form method="post" action="/submit">
        <label>Name:</label><br>
        <input type="text" name="patient_name" required><br>

        <label>Phone:</label><br>
        <input type="text" name="phone" required><br>

        <label>Date of Birth:</label><br>
        <input type="date" name="dob" required><br>

        <label>Insurance Number:</label><br>
        <input type="text" name="insurance"><br>

        <label>Reason for Checkup:</label><br>
        <select name="reason">
            <option value="Flu-like symptoms">Flu-like symptoms</option>
            <option value="Minor laceration">Minor laceration</option>
            <option value="COVID-19 test">COVID-19 test</option>
            <option value="Common infections (ear, pink eye)">Common infections (ear, pink eye)</option>
            <option value="Sore throat / strep check">Sore throat / strep check</option>
            <option value="Sprain/strain">Sprain/strain</option>
            <option value="Rash or allergic reaction (mild)">Rash or allergic reaction (mild)</option>
            <option value="Urinary symptoms (possible UTI)">Urinary symptoms (possible UTI)</option>
            <option value="Medication refill/quick consult">Medication refill/quick consult</option>
        </select><br>

        <input type="submit" value="Join Queue">
    </form>
    <div class="info">
        <p><strong>Note:</strong> After registering, please check in with staff when you arrive at the clinic.</p>
    </div>
</body>
</html>
"""

result_html = """
<!doctype html>
<html>
<head>
    <title>Check-In Confirmation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
        h2 { color: #28a745; }
        .result {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            max-width: 500px;
        }
        .back-btn {
            margin-top: 20px;
            display: inline-block;
            text-decoration: none;
            background-color: #007bff;
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
        }
        .back-btn:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="result">
        <h2>Check-In Successful!</h2>
        <p><strong>Queue Position:</strong> {{ position }}</p>
        <p><strong>Expected Start:</strong> {{ expected_start_time }}</p>
        <p><strong>Expected End:</strong> {{ expected_end_time }}</p>
        <p><strong>Estimated Duration:</strong> {{ expected_duration_minutes }} minutes</p>
        <p style="font-size: 18px;"><strong>Estimated Wait:</strong> {{ initial_wait_minutes }} minutes</p>
        <p><strong>Check in by:</strong> {{ check_in_by }}</p>
        <a href="/" class="back-btn">← Back to Check-In</a>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(form_html)

@app.route("/submit", methods=["POST"])
def submit():
    data = {
        "patient_name": request.form["patient_name"],
        "phone": request.form["phone"],
        "dob": request.form["dob"],
        "insurance": request.form["insurance"],
        "reason": request.form["reason"]
    }

    try:
        # Send data to backend
        response = requests.post("http://127.0.0.1:5001/api/patient/joinqueue", data=data)
        resp_json = response.json()
    except Exception as e:
        return f"<p>Error connecting to backend: {e}</p>", 500

    # Handle backend JSON response gracefully
    position = resp_json.get("position", "N/A")
    # Display queue position starting at 1 for users
    if isinstance(position, int):
        position = position + 1
    expected_start_time = resp_json.get("expected_start_time") or resp_json.get("scheduled_time", "Unknown")
    expected_end_time = resp_json.get("expected_end_time", "Unknown")
    expected_duration_minutes = resp_json.get("expected_duration_minutes", "N/A")
    initial_wait_minutes = resp_json.get("initial_wait_minutes", "N/A")
    check_in_by = resp_json.get("check_in_by", "N/A")

    return render_template_string(
        result_html,
        position=position,
        expected_start_time=expected_start_time,
        expected_end_time=expected_end_time,
        expected_duration_minutes=expected_duration_minutes,
        initial_wait_minutes=initial_wait_minutes,
        check_in_by=check_in_by
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)