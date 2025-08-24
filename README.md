# QA-Chat-Bot  

An intelligent chatbot application that enables **natural language queries on CSV datasets** using **Google Gemini + DuckDB**, with a **web-based login & chat interface**.  

---

## ✨ Features  

✅ **Natural Language → SQL** using Google Gemini  
✅ **DuckDB backend** for high-performance analytics  
✅ **Role-based filtering**  
   - **Buyer** → Only their own purchase orders  
   - **Program Manager** → Only their managed buyers  
   - **Admin** → Full access  
✅ **Automatic data refresh** from CSV → DuckDB every 2 hours  
✅ **Modern Web UI**  
   - **Login page** (email + role)  
   - **Chat interface** with attractive bubbles & floating send button  
   - **Tables rendered in HTML** (not just raw markdown)  
✅ **Configurable via `.env`** – no code changes needed  

---

## 📂 Project Structure  

├── app.py # Flask API & web app entry point
├── data_controller.py # Handles CSV → DuckDB loading & refresh
├── llm_controller.py # Gemini integration: NL→SQL + results formatting
├── prompt.txt # Prompt template for Gemini
├── po_details.csv # Example dataset (Purchase Orders)
├── requirements.txt # Python dependencies
├── .env # Environment configuration (keys, paths)
├── templates/
│ ├── login.html # Login page (email + role)
│ └── chat.html # Chat UI (bubbles + floating send button)
└── README.md # Project documentation


## ⚙️ Setup  

1. Create & Activate Virtual Environment  

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

2. Install Dependencies

pip install -r requirements.txt


💻 Usage
🔑 Step 1: Login

Open http://127.0.0.1:5000

Enter Email + select Role

Redirected to Chat Interface

💬 Step 2: Ask Questions

Example:

Request:

What is the total spend with Vendor X this month?


Response (UI):

Summary:

Your total spend with Vendor X this month is $25,000.

Table (rendered beautifully):

PO Number	Vendor	Total Amount
PO61773	Vendor X	10,000
PO74305	Vendor X	15,000


## 📸 Screenshots

### 🔐 Login Page  
![Login Page](assets/login.png)  

### 💬 Chat Interface  
![Chat Interface](assets/chat.png)


📡 API Usage (Optional – direct endpoint)

 Endpoint:
POST /query

 Request:

{
  "user_question": "List the top 5 distinct PO numbers",
  "user_email": "andre.warren@alphatech.com",
  "role": "buyer"
}


 Response:

{
  "markdown_table": "| PO Number   |\n|:------------|\n| PO61773     |\n| PO74305     |\n| PO78437     |\n| PO89895     |\n| PO55995     |",
  "summary": "The top 5 PO numbers are PO61773, PO74305, PO78437, PO89895, and PO55995."
}
