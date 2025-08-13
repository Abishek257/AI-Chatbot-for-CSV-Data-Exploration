import logging
import duckdb
import google.generativeai as genai
import pandas as pd
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("llm_controller.log"),
        logging.StreamHandler()
    ]
)

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.error("GEMINI_API_KEY is missing in .env file")
else:
    genai.configure(api_key=api_key)

model_name = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
model = genai.GenerativeModel(model_name)

# Constants from .env
PROMPT_FILE = os.getenv("PROMPT_FILE", "prompt.txt")
DB_FILE = os.getenv("DB_FILE", "data.duckdb")
TABLE_NAME = os.getenv("TABLE_NAME", "data")

# Read prompt template
try:
    with open(PROMPT_FILE, "r") as f:
        base_prompt_template = f.read()
except FileNotFoundError:
    logging.error(f"Prompt file {PROMPT_FILE} not found.")
    base_prompt_template = ""

# Gemini: NL to SQL
def generate_sql_from_prompt(user_question, table_name):
    if not base_prompt_template:
        logging.error("Prompt template is empty.")
        return None

    prompt = (
        base_prompt_template
        .replace("{table_name}", table_name)
        .replace("{question}", user_question)
    )
    try:
        response = model.generate_content(prompt)
        raw_sql = response.text.strip()
        # Remove Markdown code fences (```sql ... ```)
        cleaned_sql = re.sub(r"```[a-zA-Z]*", "", raw_sql).replace("```", "").strip()
        return cleaned_sql
    except Exception as e:
        logging.error(f"Error generating SQL: {e}")
        return None

# Inject role-based WHERE clause
def apply_role_filter(sql_query: str, role: str, user_email: str):
    role = role.lower().strip()
    safe_email = user_email.replace("'", "''")  # prevent SQL injection
    where_clause = ""

    if role == "buyer":
        where_clause = f"\"Buyer Email\" = '{safe_email}'"
    elif role == "program manager":
        where_clause = f"\"Purchasing Manager Email\" = '{safe_email}'"
    elif role == "admin":
        return sql_query  # No filtering
    else:
        logging.warning(f"Unknown role '{role}'. No filter applied.")
        return sql_query

    sql_cleaned = sql_query.rstrip(';')
    clause_match = re.search(r"\b(group by|order by|limit)\b", sql_cleaned, re.IGNORECASE)

    if clause_match:
        idx = clause_match.start()
        before = sql_cleaned[:idx].rstrip()
        after = sql_cleaned[idx:]
        if "where" in before.lower():
            before += f" AND {where_clause} "
        else:
            before += f" WHERE {where_clause} "
        return before + after
    else:
        if "where" in sql_cleaned.lower():
            return sql_cleaned + f" AND {where_clause}"
        else:
            return sql_cleaned + f" WHERE {where_clause}"

# Execute SQL on DuckDB
def run_sql(sql_query: str):
    try:
        with duckdb.connect(DB_FILE) as con:
            df = con.execute(sql_query).fetchdf()
        return df
    except Exception as e:
        logging.error(f"SQL Execution Error: {e}")
        return None

# NL Summary for small result sets
def summarize_result(user_question: str, df: pd.DataFrame):
    markdown_table = df.to_markdown(index=False)
    prompt = f"""
User question: "{user_question}"

Query Result:
{markdown_table}

Provide a concise, natural language answer to the user based on this result.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip(), markdown_table
    except Exception as e:
        logging.error(f"Error summarizing result: {e}")
        return None, markdown_table

# Main function for POST request
def process_user_request(request_json):
    try:
        user_question = request_json.get("user_question", "").strip()
        user_email = request_json.get("user_email", "").strip()
        role = request_json.get("role", "").strip()

        if not user_question or not user_email or not role:
            return {"error": "Missing required fields: user_question, user_email, role."}

        logging.info(f"Received question from {role}: {user_question}")

        # Step 1: Generate SQL
        sql_query = generate_sql_from_prompt(user_question, TABLE_NAME)
        if not sql_query:
            return {"error": "Could not generate SQL."}

        logging.info(f"Generated SQL:\n{sql_query}")

        # Step 2: Apply role-based filter
        filtered_sql = apply_role_filter(sql_query, role, user_email)
        logging.info(f"Final SQL with filters:\n{filtered_sql}")

        # Step 3: Execute SQL
        result_df = run_sql(filtered_sql)
        if result_df is None:
            return {"error": "SQL execution failed."}

        # Step 4: Format response
        if len(result_df) > 10:
            return {
                "summary": "",
                "markdown_table": result_df.to_markdown(index=False)
            }
        else:
            summary, markdown = summarize_result(user_question, result_df)
            return {
                "summary": summary,
                "markdown_table": markdown
            }

    except Exception as e:
        logging.exception(f"Unhandled exception: {e}")
        return {"error": "Internal server error."}
