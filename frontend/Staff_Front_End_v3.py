"""
Filename: Staff_Front_End_v3.py
Author: Niranjan Vijay Badhe
Contributers: Kush Parmar, John Kadian Anthony
Last Update: 30 November 2025
Description: Frontend module for UrgentCareQ staff dashboard UI
"""

from flask import Flask, render_template_string, request, redirect, url_for
import requests

app = Flask(__name__)

staff_html = """
<!doctype html>
<html>
<head>
    <title>UrgentCare Queue - Staff Dashboard</title>
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
        }

        .header {
            background: white;
            border-bottom: 1px solid #e5e7eb;
            padding: 20px 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }

        .header h1 {
            font-size: 24px;
            font-weight: 600;
            color: #111827;
        }

        .header-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .refresh-btn {
            background: #10b981;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .refresh-btn:hover {
            background: #059669;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }

        .search-bar {
            background: white;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            margin-bottom: 24px;
        }

        .search-bar input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.2s ease;
        }

        .search-bar input:focus {
            outline: none;
            border-color: #10b981;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        }

        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            text-align: center;
        }

        .stat-card label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .stat-card .value {
            font-size: 32px;
            font-weight: 700;
            color: #111827;
        }

        .queue-container {
            display: grid;
            gap: 16px;
            margin-bottom: 24px;
        }

        .patient-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            padding: 20px;
            transition: all 0.2s ease;
            border-left: 4px solid #10b981;
        }

        .patient-card:hover {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        }

        .patient-card.waiting {
            border-left-color: #f59e0b;
        }

        .patient-card.checked_in {
            border-left-color: #3b82f6;
        }

        .patient-card.admitted {
            border-left-color: #10b981;
        }

        .patient-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .patient-info {
            flex: 1;
        }

        .patient-name {
            font-size: 20px;
            font-weight: 600;
            color: #111827;
            margin-bottom: 4px;
        }

        .patient-meta {
            font-size: 14px;
            color: #6b7280;
        }

        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-badge.waiting {
            background: #fef3c7;
            color: #92400e;
        }

        .status-badge.checked_in {
            background: #dbeafe;
            color: #1e40af;
        }

        .status-badge.admitted {
            background: #d1fae5;
            color: #065f46;
        }

        .patient-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
            padding-top: 16px;
            border-top: 1px solid #f3f4f6;
        }

        .detail-item {
            font-size: 14px;
        }

        .detail-item label {
            display: block;
            font-weight: 600;
            color: #6b7280;
            margin-bottom: 4px;
        }

        .detail-item .value {
            color: #111827;
        }

        .action-buttons {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .btn {
            flex: 1;
            min-width: 120px;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-checkin {
            background: #3b82f6;
            color: white;
        }

        .btn-checkin:hover {
            background: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }

        .btn-admit {
            background: #10b981;
            color: white;
        }

        .btn-admit:hover {
            background: #059669;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }

        .btn-checkout {
            background: #6b7280;
            color: white;
        }

        .btn-checkout:hover {
            background: #4b5563;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(107, 114, 128, 0.2);
        }

        .reset-section {
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            padding: 24px;
            text-align: center;
            border: 2px solid #ef4444;
        }

        .reset-section h3 {
            color: #ef4444;
            margin-bottom: 8px;
        }

        .reset-section p {
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 16px;
        }

        .btn-reset {
            background: #ef4444;
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-reset:hover {
            background: #dc2626;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
        }

        .empty-state {
            background: white;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            color: #6b7280;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        .empty-state-icon {
            font-size: 64px;
            margin-bottom: 16px;
            opacity: 0.3;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 20px;
            }

            .action-buttons {
                flex-direction: column;
            }

            .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-title">
                <h1>UrgentCare Queue - Staff Dashboard</h1>
            </div>
            <form method="get" action="/" style="margin: 0;">
                <button type="submit" class="refresh-btn">Refresh Queue</button>
            </form>
        </div>
    </div>

    <div class="container">
        <div class="search-bar">
            <input type="text" id="searchInput" placeholder="Search patient by name..." onkeyup="filterPatients()">
        </div>

        {% if queue_data %}
        <div class="stats-bar">
            <div class="stat-card">
                <label>Waiting</label>
                <div class="value">{{ queue_data.waiting_count }}</div>
            </div>
            <div class="stat-card">
                <label>Checked In</label>
                <div class="value">{{ queue_data.checkedin_count }}</div>
            </div>
            <div class="stat-card">
                <label>Admitted</label>
                <div class="value">{{ queue_data.admitted_count }}</div>
            </div>
            <div class="stat-card">
                <label>Total Patients</label>
                <div class="value">{{ queue_data.total_patients }}</div>
            </div>
        </div>

        <div class="queue-container" id="queueContainer">
            {% if queue_data.patients %}
                {% for patient in queue_data.patients %}
                <div class="patient-card {{ patient.status }}" data-name="{{ patient.name|lower }}">
                    <div class="patient-card-header">
                        <div class="patient-info">
                            <div class="patient-name">{{ patient.name }}</div>
                            <div class="patient-meta">Position: #{{ patient.position + 1 }} • DOB: {{ patient.dob }}</div>
                        </div>
                        <span class="status-badge {{ patient.status }}">
                            {% if patient.status == 'waiting' %}Waiting{% endif %}
                            {% if patient.status == 'checked_in' %}Checked In{% endif %}
                            {% if patient.status == 'admitted' %}Admitted{% endif %}
                        </span>
                    </div>

                    <div class="patient-details">
                        <div class="detail-item">
                            <label>Reason</label>
                            <div class="value">{{ patient.reason }}</div>
                        </div>
                        <div class="detail-item">
                            <label>Phone</label>
                            <div class="value">{{ patient.phone }}</div>
                        </div>
                        <div class="detail-item">
                            <label>Expected Start</label>
                            <div class="value">{{ patient.expected_start_time }}</div>
                        </div>
                        <div class="detail-item">
                            <label>Expected Duration</label>
                            <div class="value">{{ patient.expected_duration_minutes }} min</div>
                        </div>
                    </div>

                    <div class="action-buttons">
                        {% if patient.status == 'waiting' %}
                        <form method="post" action="/checkin" style="flex: 1; min-width: 120px;">
                            <input type="hidden" name="patient_name" value="{{ patient.name }}">
                            <input type="hidden" name="dob" value="{{ patient.dob }}">
                            <button type="submit" class="btn btn-checkin">Check In</button>
                        </form>
                        {% endif %}

                        {% if patient.status == 'checked_in' %}
                        <form method="post" action="/admit" style="flex: 1; min-width: 120px;">
                            <input type="hidden" name="patient_name" value="{{ patient.name }}">
                            <button type="submit" class="btn btn-admit">Admit Patient</button>
                        </form>
                        {% endif %}

                        {% if patient.status == 'admitted' %}
                        <form method="post" action="/checkout" style="flex: 1; min-width: 120px;">
                            <input type="hidden" name="patient_name" value="{{ patient.name }}">
                            <button type="submit" class="btn btn-checkout">Check Out</button>
                        </form>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <div class="empty-state-icon">—</div>
                    <h3>No patients in queue</h3>
                    <p>Queue is empty. New patients will appear here.</p>
                </div>
            {% endif %}
        </div>
        {% endif %}

        <div class="reset-section">
            <h3>Reset Queue</h3>
            <p>This will permanently delete all patients from the queue. This action cannot be undone.</p>
            <form method="post" action="/reset_queue" onsubmit="return confirm('Are you sure you want to reset the queue? This will remove all patients.')">
                <button type="submit" class="btn-reset">Reset Queue</button>
            </form>
        </div>
    </div>

    <script>
        function filterPatients() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.patient-card');

            cards.forEach(card => {
                const name = card.getAttribute('data-name');
                if (name.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""


def get_queue_data():
    try:
        response = requests.get("http://127.0.0.1:5001/api/staff/queue")
        if response.status_code == 200:
            data = response.json()

            # Calculate status counts
            patients = data.get("patients", [])
            waiting_count = sum(1 for p in patients if p.get("status") == "waiting")
            checkedin_count = sum(1 for p in patients if p.get("status") == "checked_in")
            admitted_count = sum(1 for p in patients if p.get("status") == "admitted")

            # Format times for display
            for patient in patients:
                if patient.get("expected_start_time"):
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(patient["expected_start_time"])
                        patient["expected_start_time"] = dt.strftime("%I:%M %p")
                    except:
                        pass

            return {
                "patients": patients,
                "total_patients": data.get("total_patients", 0),
                "waiting_count": waiting_count,
                "checkedin_count": checkedin_count,
                "admitted_count": admitted_count,
                "global_delay_minutes": data.get("global_delay_minutes", 0)
            }
    except Exception as e:
        print(f"Error fetching queue: {e}")
    return None


@app.route("/", methods=["GET"])
def index():
    queue_data = get_queue_data()
    return render_template_string(staff_html, queue_data=queue_data)


@app.route("/checkin", methods=["POST"])
def checkin():
    name = request.form.get("patient_name", "").strip()
    dob = request.form.get("dob", "").strip()

    try:
        data = {"patient_name": name}
        if dob:
            data["dob"] = dob

        response = requests.post("http://127.0.0.1:5001/api/patient/checkin", data=data)

    except Exception as e:
        print(f"Error: {e}")

    # Redirect to refresh the page
    return redirect(url_for('index'))


@app.route("/admit", methods=["POST"])
def admit():
    name = request.form.get("patient_name", "").strip()

    try:
        requests.post("http://127.0.0.1:5001/api/staff/admit", data={"patient_name": name})
    except Exception as e:
        print(f"Error: {e}")

    return redirect(url_for('index'))


@app.route("/checkout", methods=["POST"])
def checkout():
    name = request.form.get("patient_name", "").strip()

    try:
        requests.post("http://127.0.0.1:5001/api/staff/checkout", data={"patient_name": name})
    except Exception as e:
        print(f"Error: {e}")

    return redirect(url_for('index'))


@app.route("/reset_queue", methods=["POST"])
def reset_queue():
    try:
        requests.post("http://127.0.0.1:5001/api/staff/reset")
    except Exception as e:
        print(f"Error: {e}")

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=5002)
