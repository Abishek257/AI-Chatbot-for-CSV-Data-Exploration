from flask import Flask, request, jsonify
import logging
from data_controller import load_csv_into_duckdb, start_data_refresh_scheduler
from llm_controller import process_user_request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Initialize Flask app
app = Flask(__name__)

# Load initial data and start scheduler
load_csv_into_duckdb()
start_data_refresh_scheduler()
logging.info("CSV loaded and scheduler started.")

# API endpoint
@app.route("/query", methods=["POST"])
def query():
    if request.is_json:
        data = request.get_json()
        logging.info(f"Incoming request: {data}")
        result = process_user_request(data)
        return jsonify(result)
    else:
        logging.warning("Invalid request format. JSON expected.")
        return jsonify({"error": "Request must be in JSON format."}), 400

# Start the Flask server
if __name__ == "__main__":
    logging.info("Starting Flask app on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
