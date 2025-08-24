from flask import Flask, request, jsonify, render_template
import logging
from data_controller import load_csv_into_duckdb, start_data_refresh_scheduler
from llm_controller import process_user_request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

app = Flask(__name__, template_folder="templates")

load_csv_into_duckdb()
start_data_refresh_scheduler()

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/query", methods=["POST"])
def query():
    if request.is_json:
        data = request.get_json()
        logging.info(f"Incoming request: {data}")
        result = process_user_request(data)
        return jsonify(result)
    else:
        return jsonify({"error": "Request must be in JSON format."}), 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
