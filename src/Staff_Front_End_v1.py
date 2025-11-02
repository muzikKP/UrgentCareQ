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
        .result {
            margin-top: 20px;
            background: #e9f7ef;
            padding: 15px;
            border-radius: 8px;
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

        {% if result %}
        <div class="result">
            <h3>Search Result:</h3>
            <p>{{ result }}</p>
        </div>
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
        response = requests.get(f"http://127.0.0.1:5001/api/staff/search", params={"name": name})
        if response.status_code != 200:
            result_text = f"Backend error: {response.status_code} - {response.text[:100]}"
        else:
            search_data = response.json()
            matches = search_data.get("patients", [])
            result_text = f"Found {len(matches)} patient(s)" if matches else "No patients found."
    except Exception as e:
        result_text = f"Error: {e}"
    return render_template_string(staff_html, result=result_text)

@app.route("/show_queue", methods=["GET"])
def show_queue():
    try:
        response = requests.get("http://127.0.0.1:5001/api/staff/queue")
        if response.status_code != 200:
            result_text = f"Backend error: {response.status_code} - {response.text[:100]}"
        else:
            queue_data = response.json()
            result_text = f"Total patients: {queue_data.get('total_patients', 0)}"
    except Exception as e:
        result_text = f"Error: {e}"
    return render_template_string(staff_html, result=result_text)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
