from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

home_html = """
<!doctype html>
<html>
<head>
    <title>Urgent Care Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
        h2 { color: #007bff; }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            max-width: 400px;
            text-align: center;
        }
        .btn {
            display: block;
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 16px;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .btn-secondary {
            background-color: #28a745;
        }
        .btn-secondary:hover {
            background-color: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Urgent Care Portal</h2>
        <p>Please select an option:</p>
        <a href="/register" class="btn">New Patient Registration</a>
        <a href="/signin" class="btn btn-secondary">Sign In (I'm Already Registered)</a>
    </div>
</body>
</html>
"""

form_html = """
<!doctype html>
<html>
<head>
    <title>Patient Registration</title>
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
        .back-link {
            margin-top: 15px;
            display: inline-block;
            color: #007bff;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <h2>New Patient Registration</h2>
    <form method="post" action="/submit">
        <label>Name:</label><br>
        <input type="text" name="patient_name" required><br>

        <label>Phone:</label><br>
        <input type="text" name="phone" required><br>

        <label>Date of Birth:</label><br>
        <input type="date" name="dob" required><br>

        <label>Insurance Number:</label><br>
        <input type="text" name="insurance"><br>

        <label>Symptoms:</label><br>
        <textarea name="symptoms" rows="3"></textarea><br>

        <input type="submit" value="Register & Join Queue">
    </form>
    <a href="/" class="back-link">← Back to Home</a>
</body>
</html>
"""

signin_html = """
<!doctype html>
<html>
<head>
    <title>Patient Sign In</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
        h2 { color: #28a745; }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            max-width: 400px;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-top: 4px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        input[type="submit"] {
            width: 100%;
            background-color: #28a745;
            color: white;
            cursor: pointer;
            border: none;
            padding: 12px;
            border-radius: 6px;
            font-size: 16px;
        }
        input[type="submit"]:hover {
            background-color: #218838;
        }
        .back-link {
            margin-top: 15px;
            display: inline-block;
            color: #007bff;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Sign In</h2>
        <p>Enter your full name to mark yourself as present:</p>
        <form method="post" action="/signin_submit">
            <label>Full Name:</label><br>
            <input type="text" name="patient_name" placeholder="e.g., John Doe" required><br>
            <input type="submit" value="Sign In">
        </form>
        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
"""

signin_success_html = """
<!doctype html>
<html>
<head>
    <title>Sign In Successful</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
        h2 { color: #28a745; }
        .result {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            max-width: 500px;
        }
        .success { color: #28a745; }
        .error { color: #dc3545; }
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
        {% if success %}
        <h2 class="success">✓ Sign In Successful!</h2>
        <p><strong>Welcome, {{ name }}!</strong></p>
        <p>You have been marked as present.</p>
        {% if scheduled_time %}
        <p><strong>Your Scheduled Time:</strong> {{ scheduled_time }}</p>
        {% endif %}
        {% else %}
        <h2 class="error">Sign In Failed</h2>
        <p>{{ message }}</p>
        {% endif %}
        <a href="/" class="back-btn">← Back to Home</a>
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
        <p><strong>Scheduled Time:</strong> {{ scheduled_time }}</p>
        <p><strong>Estimated Wait:</strong> {{ estimated_wait_minutes }} minutes</p>
        <a href="/" class="back-btn">← Back to Check-In</a>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(home_html)

@app.route("/register")
def register():
    return render_template_string(form_html)

@app.route("/signin")
def signin():
    return render_template_string(signin_html)

@app.route("/signin_submit", methods=["POST"])
def signin_submit():
    name = request.form.get("patient_name", "").strip()
    
    if not name:
        return render_template_string(
            signin_success_html,
            success=False,
            message="Please enter your name."
        )
    
    try:
        # Call backend API to mark patient as checked in
        response = requests.post(
            "http://127.0.0.1:5001/api/patient/checkin",
            data={"patient_name": name}
        )
        resp_json = response.json()
        
        if response.status_code == 200:
            return render_template_string(
                signin_success_html,
                success=True,
                name=name,
                scheduled_time=resp_json.get("scheduled_time", "Unknown")
            )
        else:
            return render_template_string(
                signin_success_html,
                success=False,
                message=resp_json.get("error", "Patient not found in queue.")
            )
    except Exception as e:
        return render_template_string(
            signin_success_html,
            success=False,
            message=f"Error connecting to backend: {e}"
        )

@app.route("/submit", methods=["POST"])
def submit():
    data = {
        "patient_name": request.form["patient_name"],
        "phone": request.form["phone"],
        "dob": request.form["dob"],
        "insurance": request.form["insurance"],
        "symptoms": request.form["symptoms"]
    }

    try:
        # Send data to backend
        response = requests.post("http://127.0.0.1:5001/api/patient/joinqueue", data=data)
        resp_json = response.json()
    except Exception as e:
        return f"<p>Error connecting to backend: {e}</p>", 500

    # Handle backend JSON response gracefully
    position = resp_json.get("position", "N/A")
    scheduled_time = resp_json.get("scheduled_time", "Unknown")
    estimated_wait = resp_json.get("estimated_wait_minutes", "N/A")

    return render_template_string(
        result_html,
        position=position,
        scheduled_time=scheduled_time,
        estimated_wait_minutes=estimated_wait
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)