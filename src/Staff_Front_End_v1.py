from flask import Flask, render_template_string, request

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
    # For now, just display what user typed (backend guy will connect this later)
    result_text = f"Searched for patient: {name}" if name else "No name entered."
    return render_template_string(staff_html, result=result_text)

@app.route("/show_queue", methods=["GET"])
def show_queue():
    # Placeholder: backend guy will later pull queue info here
    result_text = "Queue display placeholder (backend integration pending)."
    return render_template_string(staff_html, result=result_text)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
