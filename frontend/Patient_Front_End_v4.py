"""
Filename: Patient_Front_End_v4.py
Author: Niranjan Vijay Badhe
Contributers: John Kadian Anthony, Kush Parmar
Last Update: 30 November 2025
Description: Frontend module for UrgentCareQ patient check-in UI
"""

from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

form_html = """
<!doctype html>
<html>
<head>
    <title>UrgentCare Queue - Patient Registration</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
            overflow: hidden;
        }

        .header {
            background: #10b981;
            color: white;
            padding: 32px 24px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 4px;
            letter-spacing: -0.5px;
        }

        .header p {
            font-size: 14px;
            opacity: 0.95;
            font-weight: 500;
        }

        .form-content {
            padding: 32px 24px;
        }

        .form-group {
            margin-bottom: 24px;
        }

        label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }

        input[type="text"],
        input[type="date"],
        select,
        textarea {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.2s ease;
            background: white;
            font-family: inherit;
        }

        input[type="text"]:focus,
        input[type="date"]:focus,
        select:focus,
        textarea:focus {
            outline: none;
            border-color: #10b981;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        }

        select {
            cursor: pointer;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L6 6L11 1' stroke='%23333' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 16px center;
            padding-right: 40px;
        }

        textarea {
            min-height: 80px;
            resize: vertical;
        }

        #otherReasonGroup {
            display: none;
            margin-top: 12px;
        }

        .submit-btn {
            width: 100%;
            padding: 16px;
            background: #10b981;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 8px;
        }

        .submit-btn:hover {
            background: #059669;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }

        .submit-btn:active {
            transform: translateY(0);
        }

        .info-box {
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            padding: 16px;
            border-radius: 8px;
            margin-top: 24px;
        }

        .info-box p {
            font-size: 14px;
            color: #555;
            line-height: 1.6;
        }

        @media (max-width: 600px) {
            .header h1 {
                font-size: 24px;
            }

            .form-content {
                padding: 24px 20px;
            }
        }
    </style>
    <script>
        function toggleOtherReason() {
            const select = document.querySelector('select[name="reason"]');
            const otherGroup = document.getElementById('otherReasonGroup');
            const otherInput = document.getElementById('otherReasonInput');

            if (select.value === 'Other') {
                otherGroup.style.display = 'block';
                otherInput.required = true;
            } else {
                otherGroup.style.display = 'none';
                otherInput.required = false;
                otherInput.value = '';
            }
        }

        function handleSubmit(event) {
            const select = document.querySelector('select[name="reason"]');
            const otherInput = document.getElementById('otherReasonInput');

            if (select.value === 'Other' && otherInput.value.trim()) {
                select.value = otherInput.value.trim();
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>UrgentCare Queue</h1>
            <p>Patient Registration</p>
        </div>

        <div class="form-content">
            <form method="post" action="/submit" onsubmit="handleSubmit(event)">
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" name="patient_name" placeholder="John Doe" required>
                </div>

                <div class="form-group">
                    <label>Phone Number</label>
                    <input type="text" name="phone" placeholder="(555) 123-4567" required>
                </div>

                <div class="form-group">
                    <label>Date of Birth</label>
                    <input type="date" name="dob" required>
                </div>

                <div class="form-group">
                    <label>Insurance Number</label>
                    <input type="text" name="insurance" placeholder="Optional">
                </div>

                <div class="form-group">
                    <label>Reason for Visit</label>
                    <select name="reason" required onchange="toggleOtherReason()">
                        <option value="">Select a reason...</option>
                        <option value="Flu-like symptoms">Flu-like symptoms</option>
                        <option value="Minor laceration">Minor laceration</option>
                        <option value="COVID-19 test">COVID-19 test</option>
                        <option value="Common infections (ear, pink eye)">Common infections (ear, pink eye)</option>
                        <option value="Sore throat / strep check">Sore throat / strep check</option>
                        <option value="Sprain/strain">Sprain/strain</option>
                        <option value="Rash or allergic reaction (mild)">Rash or allergic reaction (mild)</option>
                        <option value="Urinary symptoms (possible UTI)">Urinary symptoms (possible UTI)</option>
                        <option value="Medication refill/quick consult">Medication refill/quick consult</option>
                        <option value="Other">Other</option>
                    </select>

                    <div id="otherReasonGroup">
                        <label style="margin-top: 12px;">Please specify</label>
                        <textarea id="otherReasonInput" placeholder="Describe your symptoms..."></textarea>
                    </div>
                </div>

                <button type="submit" class="submit-btn">Join Queue</button>

                <div class="info-box">
                    <p><strong>Note:</strong> After registering, please check in with staff when you arrive at the clinic.</p>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""

result_html = """
<!doctype html>
<html>
<head>
    <title>UrgentCare Queue - Confirmation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
            overflow: hidden;
        }

        .header {
            background: #10b981;
            color: white;
            padding: 32px 24px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .header p {
            font-size: 14px;
            opacity: 0.95;
        }

        .content {
            padding: 32px 24px;
        }

        .success-icon {
            width: 80px;
            height: 80px;
            background: #10b981;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            font-size: 48px;
            color: white;
            font-weight: 300;
        }

        .position-card {
            background: #10b981;
            color: white;
            padding: 24px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 24px;
        }

        .position-card h2 {
            font-size: 16px;
            font-weight: 500;
            opacity: 0.95;
            margin-bottom: 8px;
        }

        .position-number {
            font-size: 56px;
            font-weight: 700;
            line-height: 1;
        }

        .info-grid {
            display: grid;
            gap: 16px;
            margin-bottom: 24px;
        }

        .info-item {
            background: #f9fafb;
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid #10b981;
        }

        .info-item label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .info-item .value {
            font-size: 18px;
            font-weight: 600;
            color: #111827;
        }

        .back-btn {
            display: block;
            width: 100%;
            padding: 16px;
            background: white;
            color: #10b981;
            border: 2px solid #10b981;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            text-align: center;
            text-decoration: none;
            transition: all 0.2s ease;
        }

        .back-btn:hover {
            background: #10b981;
            color: white;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }

        @media (max-width: 600px) {
            .header h1 {
                font-size: 24px;
            }

            .position-number {
                font-size: 48px;
            }

            .content {
                padding: 24px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>UrgentCare Queue</h1>
            <p>Registration Confirmed</p>
        </div>

        <div class="content">
            <div class="success-icon">✓</div>

            <div class="position-card">
                <h2>Your Queue Position</h2>
                <div class="position-number">{{ position }}</div>
            </div>

            <div class="info-grid">
                <div class="info-item">
                    <label>Estimated Wait Time</label>
                    <div class="value">{{ initial_wait_minutes }} minutes</div>
                </div>

                <div class="info-item">
                    <label>Check In By</label>
                    <div class="value">{{ check_in_by }}</div>
                </div>
            </div>

            <a href="/" class="back-btn">← Register Another Patient</a>
        </div>
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
        "insurance": request.form.get("insurance", ""),
        "reason": request.form["reason"]
    }

    try:
        response = requests.post("http://127.0.0.1:5001/api/patient/joinqueue", data=data)
        resp_json = response.json()
    except Exception as e:
        return f"<p>Error connecting to backend: {e}</p>", 500

    position = resp_json.get("position", "N/A")
    if isinstance(position, int):
        position = position + 1

    initial_wait_minutes = resp_json.get("initial_wait_minutes", "N/A")
    check_in_by = resp_json.get("check_in_by", "N/A")

    # Format check_in_by to include date and time
    if check_in_by != "N/A" and check_in_by != "ASAP":
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(check_in_by)
            check_in_by = dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            pass

    return render_template_string(
        result_html,
        position=position,
        initial_wait_minutes=initial_wait_minutes,
        check_in_by=check_in_by
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
