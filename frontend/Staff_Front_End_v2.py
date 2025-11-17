from flask import Flask, render_template_string, request
import requests
from datetime import datetime

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
            max-width: 800px;
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
        .patient-card {
            background: #ffffff;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid #ddd;
        }
        .actions button {
            margin-right: 10px;
        }
        .result-title {
            margin-top: 20px;
            font-size: 20px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Urgent Care Staff Dashboard</h2>

        <form method="post" action="/search">
            <div class="search-bar">
                <input type="text" name="search_name" placeholder="Search patient by name">
                <button type="submit">Search</button>
            </div>
        </form>

        <form method="get" action="/show_queue" style="margin-top: 20px;">
            <button type="submit">Show Queue</button>
        </form>

        {% if patients %}
            <div class="result-title">Queue:</div>
            {% for p in patients %}
                <div class="patient-card">
                    <p><strong>Name:</strong> {{ p.name }}</p>
                    <p><strong>Phone:</strong> {{ p.phone }}</p>
                    <p><strong>DOB:</strong> {{ p.dob }}</p>
                    <p><strong>Insurance:</strong> {{ p.insurance }}</p>
                    <p><strong>Symptoms:</strong> {{ p.symptoms }}</p>
                    <p><strong>Position:</strong> {{ p.position }}</p>
                    <p><strong>Scheduled Time:</strong> {{ p.scheduled_time }}</p>

                    <div class="actions">
                        <button>Checked In</button>
                        <button>Admitted</button>
                        <button>Checked Out</button>
                    </div>
                </div>
            {% endfor %}
        {% elif result %}
            <p>{{ result }}</p>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(staff_html)


@app.route("/search", methods=["POST"])
def search():
    name = request.form.get("search_name", "").strip()
    if not name:
        return render_template_string(staff_html, result="No name entered.")

    try:
        response = requests.get("http://127.0.0.1:5001/api/staff/search", params={"name": name})
        data = response.json()
        patients = data.get("patients", [])
    except Exception as e:
        return render_template_string(staff_html, result=f"Error: {e}")

    # Format scheduled time for each patient
    for p in patients:
        try:
            dt = datetime.fromisoformat(p["scheduled_time"])
            p["scheduled_time"] = dt.strftime("%I:%M %p")
        except:
            pass

    return render_template_string(staff_html, patients=patients)


@app.route("/show_queue", methods=["GET"])
def show_queue():
    try:
        response = requests.get("http://127.0.0.1:5001/api/staff/queue")
        data = response.json()
        patients = data.get("patients", [])
    except Exception as e:
        return render_template_string(staff_html, result=f"Error: {e}")

    # Make scheduled time readable
    for p in patients:
        try:
            dt = datetime.fromisoformat(p["scheduled_time"])
            p["scheduled_time"] = dt.strftime("%I:%M %p")
        except:
            pass

    return render_template_string(staff_html, patients=patients)


if __name__ == "__main__":
    app.run(debug=True, port=5002)