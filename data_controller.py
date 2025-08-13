import duckdb
import logging
import schedule
import time
import os
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# Configuration from .env or defaults
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "po_details.csv")
DB_FILE = os.getenv("DB_FILE", "data.duckdb")
TABLE_NAME = os.getenv("TABLE_NAME", "data")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("data_controller.log"),
        logging.StreamHandler()
    ]
)

def load_csv_into_duckdb():
    """Loads or refreshes CSV data into DuckDB."""
    try:
        logging.info("Starting CSV to DuckDB load process...")
        with duckdb.connect(DB_FILE) as con:
            con.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
            con.execute(f"CREATE TABLE {TABLE_NAME} AS SELECT * FROM read_csv_auto('{CSV_FILE_PATH}')")
        logging.info(f"Table '{TABLE_NAME}' created successfully in DuckDB.")
    except Exception as e:
        logging.error(f"Error loading data into DuckDB: {e}")

def start_data_refresh_scheduler():
    """Starts a background scheduler to refresh data every 2 hours."""
    schedule.every(2).hours.do(load_csv_into_duckdb)
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)
    thread = Thread(target=run_scheduler, daemon=True)
    thread.start()
    logging.info("Data refresh scheduler started (interval: 2 hours).")
