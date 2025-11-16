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
                <div class="search-bar">
                    <input type="text" name="patient_name" placeholder="Enter patient name to check in" required>
                    <button type="submit" class="btn-success">Check In</button>
                </div>
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
    
    if not name:
        return render_template_string(
            staff_html,
            result="Please enter a patient name.",
            result_class="error",
            result_title="Error"
        )
    
    try:
        # Call backend API to check in patient
        response = requests.post(
            "http://127.0.0.1:5001/api/patient/checkin",
            data={"patient_name": name}
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
    # Placeholder: backend guy will later pull queue info here
    result_text = "<p>Queue display placeholder (backend integration pending).</p>"
    return render_template_string(
        staff_html,
        result=result_text,
        result_class="",
        result_title="Queue"
    )

if __name__ == "__main__":
    app.run(debug=True, port=5002)
