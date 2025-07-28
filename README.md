# 🧠 DataTalk-AI

A powerful AI-powered SQL assistant built with **Streamlit** that allows you to:
- Generate SQL queries from natural language
- Auto-correct failed queries
- Connect to multiple types of databases
- Extract and visualize schema
- Execute queries and download results

---

## ⚙️ Features

✅ Natural language → SQL generation using **Gemini AI**  
✅ Supports **SQLite**, **MySQL**, **PostgreSQL**, and basic **MongoDB**  
✅ Schema auto-extraction  
✅ Auto-correction of failed queries  
✅ Download results as **CSV**  
✅ Real-time query execution and result preview

---

## 🏗️ Tech Stack

- Frontend: [Streamlit](https://streamlit.io/)
- Backend: Flask API (running on `http://localhost:5000`)
- AI: Gemini (Google Generative AI) or any language model via API
- Language: Python 3.9+
- Optional: Pandas, Requests, etc.

---

## 📦 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/prasadac07/DataTalk-AI.git
cd DataTalk-AI
```


### 2. Create a virtual environment

```bash
python -m venv .venv
# Activate it:
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows CMD
.venv\Scripts\activate.bat
# Linux/macOS
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the backend (Flask)

Make sure you have a Flask server running separately that supports:

* `/get_schema`
* `/generate_query`
* `/execute_query`

> Example backend repo link or API code should be added here.

### 5. Run the Streamlit app

```bash
streamlit run streamlit_app.py
```

---

## 🧪 Supported Databases

| Database   | Features                                  |
| ---------- | ----------------------------------------- |
| SQLite     | Full support, easy to set up              |
| MySQL      | Requires host/user/password/database      |
| PostgreSQL | Requires host/user/password/database      |
| MongoDB    | Basic query support for text-like queries |

---

## 📋 Usage Guide

1. **Configure your database** in the sidebar
2. Click **"🔍 Auto-Extract Schema"** or manually paste your schema
3. Type a **natural language question**
4. Click **"🚀 Generate SQL"**
5. Click **"⚡ Execute Query"** to run the query (with auto-correction if needed)
6. Optionally **download** results as CSV

---

## 📁 Folder Structure

```
.
├── streamlit_app.py         # Frontend (Streamlit UI)
├── app.py / flask_api.py    # Backend (Flask server)
├── .env                     # Environment variables (ignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📄 .gitignore Example

```gitignore
.env
.venv/
__pycache__/
*.pyc
*.db
*.sqlite3
.DS_Store
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit a pull request.

---

## 🔒 Security

Make sure you:

* Never commit `.env` files with API keys or passwords
* Use `.gitignore` to avoid uploading sensitive info

---

## 📬 Contact

For questions or suggestions, contact [Taneeee](https://github.com/Taneeee) or open an issue.

---

