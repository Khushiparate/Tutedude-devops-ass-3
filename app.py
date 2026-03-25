from flask import Flask, jsonify, request, render_template, redirect, url_for
import json
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

app = Flask(__name__)

# ─── MongoDB Atlas Configuration ───────────────────────────────────────────────
# Replace the URI below with your actual MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://admin:pass123@cluster0.xr5gp77.mongodb.net/?appName=Cluster0"
DB_NAME = "flask_assignment"
COLLECTION_NAME = "submissions"

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def get_mongo_collection():
    """Connect to MongoDB Atlas and return the collection."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]


# ─── Task 1: /api route ────────────────────────────────────────────────────────
@app.route("/api")
def api():
    """Read data from data.json and return it as a JSON list."""
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "data.json not found"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in data.json"}), 500


# ─── Task 2: Form routes ───────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    """Display the submission form."""
    return render_template("index.html", error=None)


@app.route("/submit", methods=["POST"])
def submit():
    """Handle form submission and insert into MongoDB Atlas."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
 # Basic validation
    if not name or not email or not message:
        error = "All fields are required. Please fill in name, email, and message."
        return render_template("index.html", error=error), 400

    try:
        collection = get_mongo_collection()
        document = {"name": name, "email": email, "message": message}
        collection.insert_one(document)
        # Success → redirect to success page
        return redirect(url_for("success"))

    except ConnectionFailure:
        error = "Could not connect to MongoDB Atlas. Please check your connection string."
        return render_template("index.html", error=error), 500
    except OperationFailure as e:
        error = f"Database operation failed: {str(e)}"
        return render_template("index.html", error=error), 500
    except Exception as e:
        error = f"An unexpected error occurred: {str(e)}"
        return render_template("index.html", error=error), 500


@app.route("/success")
def success():
    """Display the success page after form submission."""
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True)

