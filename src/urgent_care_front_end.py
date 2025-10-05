from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# HTML form (kept inline for simplicity)
form_html = """
<!doctype html>
<html>
<head>
    <title>Patient Check-In</title>
</head>
<body>
    <h2>Urgent Care Check-In</h2>
    <form method="post" action="/submit">
        <label>Name:</label><br>
        <input type="text" name="patient_name"><br><br>

        <label>Phone:</label><br>
        <input type="text" name="phone"><br><br>

        <label>Date of Birth:</label><br>
        <input type="date" name="dob"><br><br>

        <label>Insurance Number:</label><br>
        <input type="text" name="insurance"><br><br>

        <label>Symptoms:</label><br>
        <textarea name="symptoms"></textarea><br><br>

        <input type="submit" value="Check In">
    </form>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(form_html)

@app.route("/submit", methods=["POST"])
def submit():
    # Collect form data
    data = {
        "patient_name": request.form["patient_name"],
        "phone": request.form["phone"],
        "dob": request.form["dob"],
        "insurance": request.form["insurance"],
        "symptoms": request.form["symptoms"]
    }
    # Just return JSON to the browser
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)