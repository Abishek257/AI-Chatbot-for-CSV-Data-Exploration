# QA-Chat-Bot
Back-end of chatbot application that answers user queries based on data from CSV files.

     This project is an intelligent chatbot API that:
(1) Accepts a natural language question from the user.
(2) Uses Google Gemini to convert it into a DuckDB SQL query.
(3) Executes the query on a DuckDB database created from a CSV file.
(4) Applies role-based data filtering (Buyer, Program Manager, Admin).
(5) Returns results as a Markdown table and a natural language summary.
     
     This enables non-technical users to query CSV datasets in plain English without writing SQL.

**PROJECT STRUCTURE**

├── app.py                # Flask API entry point
├── data_controller.py    # Handles CSV → DuckDB loading & refresh
├── llm_controller.py     # Handles Gemini interaction, SQL generation, and results formatting
├── prompt.txt             # Prompt template for Gemini
├── po_details.csv         # Example CSV dataset
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
└── README.md              # Project documentation

**FEATURES**

(1) Natural Language to SQL using Google Gemini API.
(2) DuckDB backend for high-performance local analytics.
(3) Role-based data filtering:
      Buyer → Only their own purchase orders.
      Program Manager → Only their managed buyers.
      Admin → Full access.
(4) Automatic CSV → DuckDB load every 2 hours.
(5) Markdown table output for easy integration into chatbots or UIs.
(6) Configurable via .env file — no code changes needed for different datasets.

**PROCEDURE**

(1) Create & Activate Virtual Environment

python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

(2) Install Dependencies

pip install -r requirements.txt

(3) Start the API

Run the API on the host address http://127.0.0.1:5000

**API USAGE**

REQUEST:

{
  "user_question": "List the top 5 distinct PO numbers",
  "user_email": "andre.warren@alphatech.com",
  "role": "buyer"
}

RESPONSE: 

{
    "markdown_table": "| PO Number   |\n|:------------|\n| PO61773     |\n| PO74305     |\n| PO78437     |\n| PO89895     |\n| PO55995     |",
    "summary": "The top 5 PO numbers are PO61773, PO74305, PO78437, PO89895, and PO55995."
}

